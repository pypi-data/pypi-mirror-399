"""
Unit tests for godaddycheck client.
"""

import os
import pytest
from unittest.mock import Mock, patch
import httpx
from godaddycheck.client import GoDaddyClient, check, suggest, tlds


class TestClientInitialization:
    """Tests for client initialization."""

    def test_client_requires_credentials_without_env(self, monkeypatch):
        """Test that client raises error without credentials."""
        monkeypatch.delenv("GODADDY_API_KEY", raising=False)
        monkeypatch.delenv("GODADDY_API_SECRET", raising=False)

        with pytest.raises(ValueError, match="API credentials required"):
            GoDaddyClient()

    def test_client_with_env_credentials(self, mock_credentials):
        """Test client initialization with environment variables."""
        client = GoDaddyClient()
        assert client.api_key == "test_key_12345"
        assert client.api_secret == "test_secret_67890"

    def test_client_with_explicit_credentials(self):
        """Test client initialization with explicit credentials."""
        client = GoDaddyClient(api_key="my_key", api_secret="my_secret")
        assert client.api_key == "my_key"
        assert client.api_secret == "my_secret"

    def test_client_custom_config(self, mock_credentials):
        """Test client with custom configuration."""
        client = GoDaddyClient(
            api_url="https://custom.api.com",
            max_retries=5,
            timeout=60.0
        )
        assert client.api_url == "https://custom.api.com"
        assert client.max_retries == 5
        assert client.timeout == 60.0

    def test_client_with_env_api_url(self, monkeypatch):
        """Test client reads API URL from environment variable."""
        monkeypatch.setenv("GODADDY_API_KEY", "test_key")
        monkeypatch.setenv("GODADDY_API_SECRET", "test_secret")
        monkeypatch.setenv("GODADDY_API_URL", "https://api.ote-godaddy.com")

        client = GoDaddyClient()
        assert client.api_url == "https://api.ote-godaddy.com"

    def test_client_api_url_defaults_to_production(self, monkeypatch):
        """Test client defaults to production API URL when env var not set."""
        monkeypatch.setenv("GODADDY_API_KEY", "test_key")
        monkeypatch.setenv("GODADDY_API_SECRET", "test_secret")
        monkeypatch.delenv("GODADDY_API_URL", raising=False)

        client = GoDaddyClient()
        assert client.api_url == "https://api.godaddy.com"


class TestPriceNormalization:
    """Tests for price normalization."""

    def test_normalize_price_cents_to_dollars(self, mock_credentials):
        """Test converting cents to dollars."""
        client = GoDaddyClient()
        assert client._normalize_price(1299) == 12.99
        assert client._normalize_price(3999) == 39.99
        assert client._normalize_price(10000) == 100.0

    def test_normalize_price_micro_dollars(self, mock_credentials):
        """Test converting micro-dollars to dollars."""
        client = GoDaddyClient()
        # GoDaddy API returns prices in micro-dollars (1/1,000,000)
        assert client._normalize_price(423980000) == 423.98
        assert client._normalize_price(129900000) == 129.90
        assert client._normalize_price(1000000) == 1.0

    def test_normalize_price_already_dollars(self, mock_credentials):
        """Test prices already in dollars."""
        client = GoDaddyClient()
        assert client._normalize_price(12.99) == 12.99
        assert client._normalize_price(39.99) == 39.99
        assert client._normalize_price(100.0) == 100.0

    def test_normalize_price_none(self, mock_credentials):
        """Test normalizing None."""
        client = GoDaddyClient()
        assert client._normalize_price(None) is None

    def test_normalize_price_invalid(self, mock_credentials):
        """Test normalizing invalid values."""
        client = GoDaddyClient()
        assert client._normalize_price("invalid") is None
        assert client._normalize_price([]) is None
        assert client._normalize_price({}) is None

    def test_normalize_result(self, mock_credentials, sample_suggest_response):
        """Test normalizing full result."""
        client = GoDaddyClient()
        result = sample_suggest_response[0]
        normalized = client._normalize_result(result)
        assert normalized["price"] == 12.99  # Converted from 1299 cents


class TestHeaders:
    """Tests for authentication headers."""

    def test_headers_format(self, mock_credentials):
        """Test authorization header format."""
        client = GoDaddyClient()
        headers = client.headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "sso-key test_key_12345:test_secret_67890"
        assert headers["accept"] == "application/json"


class TestContextManager:
    """Tests for context manager functionality."""

    def test_context_manager_enter_exit(self, mock_credentials):
        """Test client as context manager."""
        with GoDaddyClient() as client:
            assert client is not None
            assert client._client is None  # Lazy initialization
        # Should close cleanly without error

    def test_context_manager_closes_client(self, mock_credentials):
        """Test that context manager closes HTTP client."""
        with GoDaddyClient() as client:
            # Force client creation
            _ = client.client
            assert client._client is not None

        # Client should be closed after exiting context
        assert client._client is None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch("godaddycheck.client.GoDaddyClient.check")
    def test_convenience_check(self, mock_check, mock_credentials):
        """Test convenience check function."""
        mock_check.return_value = {"domain": "test.com", "available": True}

        result = check("test.com")
        assert result["domain"] == "test.com"
        mock_check.assert_called_once_with("test.com", "FAST")

    @patch("godaddycheck.client.GoDaddyClient.suggest")
    def test_convenience_suggest(self, mock_suggest, mock_credentials):
        """Test convenience suggest function."""
        mock_suggest.return_value = [{"domain": "test.com"}]

        result = suggest("tech", limit=5)
        assert len(result) == 1
        mock_suggest.assert_called_once_with("tech", 5)

    @patch("godaddycheck.client.GoDaddyClient.tlds")
    def test_convenience_tlds(self, mock_tlds, mock_credentials):
        """Test convenience tlds function."""
        mock_tlds.return_value = [{"name": "com"}]

        result = tlds()
        assert len(result) == 1
        mock_tlds.assert_called_once()


class TestRetryLogic:
    """Tests for retry logic."""

    def test_retry_on_network_error(self, mock_credentials):
        """Test retry on network errors."""
        client = GoDaddyClient(max_retries=2)

        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"available": True}
        mock_response.raise_for_status = Mock()

        mock_http_client = Mock()
        mock_http_client.request.side_effect = [
            httpx.NetworkError("Connection failed"),
            httpx.NetworkError("Connection failed"),
            mock_response
        ]

        # Patch the _client attribute directly
        with patch.object(client, "_client", mock_http_client):
            # Should succeed after retries
            with patch("time.sleep"):  # Speed up test
                response = client._retry_request("GET", "http://test.com")
                assert response.json()["available"] is True

    def test_no_retry_on_client_error(self, mock_credentials):
        """Test no retry on 4xx client errors."""
        client = GoDaddyClient(max_retries=2)

        mock_response = Mock()
        mock_response.status_code = 400
        error = httpx.HTTPStatusError("Bad request", request=Mock(), response=mock_response)

        mock_http_client = Mock()
        mock_http_client.request.side_effect = error

        # Patch the _client attribute directly
        with patch.object(client, "_client", mock_http_client):
            # Should fail immediately without retry
            with pytest.raises(httpx.HTTPStatusError):
                client._retry_request("GET", "http://test.com")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
