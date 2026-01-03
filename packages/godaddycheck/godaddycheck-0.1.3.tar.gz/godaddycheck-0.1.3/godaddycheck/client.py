"""
GoDaddy domain availability checker client.
"""

import os
import time
from typing import List, Dict, Any, Optional
from functools import wraps
import httpx
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class GoDaddyClient:
    """Client for GoDaddy domain API operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 30.0
    ):
        """
        Initialize GoDaddy client.

        Args:
            api_key: GoDaddy API key (defaults to GODADDY_API_KEY env var)
            api_secret: GoDaddy API secret (defaults to GODADDY_API_SECRET env var)
            api_url: GoDaddy API base URL (defaults to GODADDY_API_URL env var or https://api.godaddy.com)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("GODADDY_API_KEY")
        self.api_secret = api_secret or os.getenv("GODADDY_API_SECRET")
        self.api_url = api_url or os.getenv("GODADDY_API_URL", "https://api.godaddy.com")
        self.max_retries = max_retries
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials required. Set GODADDY_API_KEY and GODADDY_API_SECRET "
                "environment variables or pass them to the constructor."
            )

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "accept": "application/json",
            "Authorization": f"sso-key {self.api_key}:{self.api_secret}"
        }

    def _normalize_price(self, price: Any) -> Optional[float]:
        """
        Normalize price to dollars.

        Args:
            price: Price value (could be in micro-dollars, cents, or dollars)

        Returns:
            Price in dollars, or None if invalid

        Note:
            GoDaddy API returns prices in different formats:
            - Micro-dollars (1/1,000,000): e.g., 423980000 = $423.98
            - Cents (1/100): e.g., 1299 = $12.99
            - Dollars: e.g., 12.99 = $12.99
        """
        if price is None:
            return None

        try:
            price_float = float(price)
            
            # Handle micro-dollars (values >= 1,000,000)
            if price_float >= 1_000_000:
                return price_float / 1_000_000
            
            # Handle cents (values >= 1000 but < 1,000,000)
            # Note: prices < 1000 are likely already in dollars
            if price_float >= 1000:
                return price_float / 100
            
            # Already in dollars
            return price_float
        except (ValueError, TypeError):
            return None

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize API result with price conversion."""
        normalized = result.copy()

        # Find and normalize price
        if "price" in normalized:
            normalized["price"] = self._normalize_price(normalized["price"])

        return normalized

    def _retry_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            HTTP response

        Raises:
            httpx.HTTPStatusError: If request fails after retries
        """
        delay = 1.0
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response

            except (httpx.HTTPStatusError, httpx.NetworkError, httpx.TimeoutException) as e:
                last_error = e

                # Check if error is retryable
                is_retryable = False
                if isinstance(e, (httpx.NetworkError, httpx.TimeoutException)):
                    is_retryable = True
                elif isinstance(e, httpx.HTTPStatusError):
                    # Retry on 429 (rate limit) and 5xx errors
                    if e.response.status_code in (429, 500, 502, 503, 504):
                        is_retryable = True

                # Don't retry on last attempt or non-retryable errors
                if attempt == self.max_retries or not is_retryable:
                    raise

                # Wait before retry with exponential backoff
                time.sleep(delay)
                delay = min(delay * 2, 10.0)

        raise last_error

    def check(self, domain: str, check_type: str = "FAST") -> Dict[str, Any]:
        """
        Check if a domain is available.

        Args:
            domain: Domain name to check (e.g., 'amankumar.ai')
            check_type: 'FAST' or 'FULL' (default: 'FAST')

        Returns:
            Dict with keys:
                - domain: str
                - available: bool
                - price: float (in dollars, if available)
                - currency: str

        Example:
            >>> client = GoDaddyClient()
            >>> result = client.check('amankumar.ai')
            >>> print(f"Available: {result['available']}, Price: ${result.get('price', 'N/A')}")
        """
        url = f"{self.api_url}/v1/domains/available"
        params = {"domain": domain, "checkType": check_type}

        response = self._retry_request("GET", url, params=params)
        result = response.json()
        return self._normalize_result(result)

    def suggest(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get domain suggestions for a keyword.

        Note: The GoDaddy API only returns domain names. To check availability
        and pricing, use the check() method for each suggested domain.

        Args:
            query: Keyword to get suggestions for
            limit: Maximum number of suggestions (default: 10)

        Returns:
            List of dicts with keys:
                - domain: str (domain name suggestion)

        Example:
            >>> client = GoDaddyClient()
            >>> suggestions = client.suggest('tech', limit=5)
            >>> for s in suggestions:
            ...     domain = s['domain']
            ...     availability = client.check(domain)
            ...     print(f"{domain}: Available={availability['available']}")
        """
        url = f"{self.api_url}/v1/domains/suggest"
        params = {"query": query, "limit": limit}

        response = self._retry_request("GET", url, params=params)
        results = response.json()

        if isinstance(results, list):
            # API only returns domain names, no normalization needed
            return results
        return results

    def tlds(self) -> List[Dict[str, Any]]:
        """
        Get list of available top-level domains (TLDs).

        Returns:
            List of dicts with TLD information including:
                - name: str (e.g., 'com', 'io', 'org')
                - type: str (TLD type)

        Example:
            >>> client = GoDaddyClient()
            >>> tlds = client.tlds()
            >>> print(f"Found {len(tlds)} TLDs")
            >>> print(tlds[:5])  # First 5 TLDs
        """
        url = f"{self.api_url}/v1/domains/tlds"

        response = self._retry_request("GET", url)
        results = response.json()

        return results if isinstance(results, list) else []

    def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions for simple usage
def check(domain: str, check_type: str = "FAST", **client_kwargs) -> Dict[str, Any]:
    """
    Check if a domain is available (convenience function).

    Args:
        domain: Domain name to check
        check_type: 'FAST' or 'FULL'
        **client_kwargs: Additional arguments for GoDaddyClient

    Returns:
        Domain availability information
    """
    with GoDaddyClient(**client_kwargs) as client:
        return client.check(domain, check_type)


def suggest(query: str, limit: int = 10, **client_kwargs) -> List[Dict[str, Any]]:
    """
    Get domain suggestions (convenience function).

    Args:
        query: Keyword for suggestions
        limit: Maximum number of suggestions
        **client_kwargs: Additional arguments for GoDaddyClient

    Returns:
        List of domain suggestions
    """
    with GoDaddyClient(**client_kwargs) as client:
        return client.suggest(query, limit)


def tlds(**client_kwargs) -> List[Dict[str, Any]]:
    """
    Get list of available TLDs (convenience function).

    Args:
        **client_kwargs: Additional arguments for GoDaddyClient

    Returns:
        List of TLDs
    """
    with GoDaddyClient(**client_kwargs) as client:
        return client.tlds()
