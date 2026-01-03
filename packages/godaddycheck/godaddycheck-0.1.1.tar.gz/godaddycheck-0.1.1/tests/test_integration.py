"""
Integration tests for godaddycheck client.

These tests require real GoDaddy API credentials.
Set GODADDY_API_KEY and GODADDY_API_SECRET environment variables to run.

Run with: pytest -m integration
Skip with: pytest -m "not integration"
"""

import pytest
from godaddycheck import GoDaddyClient, check, suggest, tlds


@pytest.mark.integration
class TestIntegrationCheck:
    """Integration tests for domain checking."""

    def test_check_unavailable_domain(self, skip_without_credentials):
        """Test checking a domain that is definitely taken."""
        client = GoDaddyClient()
        result = client.check("google.com")

        assert "domain" in result
        assert "available" in result
        assert result["available"] is False
        assert result["domain"] == "google.com"

    def test_check_with_fast_type(self, skip_without_credentials):
        """Test FAST check type."""
        client = GoDaddyClient()
        result = client.check("example.com", check_type="FAST")

        assert "domain" in result
        assert "available" in result

    def test_check_with_full_type(self, skip_without_credentials):
        """Test FULL check type."""
        client = GoDaddyClient()
        result = client.check("example.com", check_type="FULL")

        assert "domain" in result
        assert "available" in result

    def test_check_convenience_function(self, skip_without_credentials):
        """Test convenience check function."""
        result = check("example.com")

        assert "domain" in result
        assert "available" in result


@pytest.mark.integration
class TestIntegrationSuggest:
    """Integration tests for domain suggestions."""

    def test_suggest_basic(self, skip_without_credentials):
        """Test basic domain suggestions."""
        client = GoDaddyClient()
        results = client.suggest("tech", limit=5)

        assert isinstance(results, list)
        assert len(results) <= 5
        assert len(results) > 0

        # Check first result structure
        first = results[0]
        assert "domain" in first
        assert "available" in first

    def test_suggest_with_different_limits(self, skip_without_credentials):
        """Test suggestions with different limits."""
        client = GoDaddyClient()

        results_5 = client.suggest("startup", limit=5)
        results_10 = client.suggest("startup", limit=10)

        assert len(results_5) <= 5
        assert len(results_10) <= 10

    def test_suggest_price_normalization(self, skip_without_credentials):
        """Test that prices are normalized to dollars."""
        client = GoDaddyClient()
        results = client.suggest("app", limit=5)

        for result in results:
            if "price" in result and result["price"] is not None:
                # Prices should be in reasonable dollar range (not cents)
                assert result["price"] < 1000, f"Price {result['price']} looks like cents, not dollars"

    def test_suggest_convenience_function(self, skip_without_credentials):
        """Test convenience suggest function."""
        results = suggest("domain", limit=3)

        assert isinstance(results, list)
        assert len(results) <= 3


@pytest.mark.integration
class TestIntegrationTLDs:
    """Integration tests for TLD listing."""

    def test_tlds_basic(self, skip_without_credentials):
        """Test basic TLD listing."""
        client = GoDaddyClient()
        results = client.tlds()

        assert isinstance(results, list)
        assert len(results) > 0

        # Check first result structure
        first = results[0]
        assert "name" in first
        assert "type" in first

    def test_tlds_contains_common_tlds(self, skip_without_credentials):
        """Test that common TLDs are present."""
        client = GoDaddyClient()
        results = client.tlds()

        tld_names = [tld.get("name") for tld in results]

        # Check for common TLDs
        assert "com" in tld_names
        assert "org" in tld_names
        assert "net" in tld_names

    def test_tlds_convenience_function(self, skip_without_credentials):
        """Test convenience tlds function."""
        results = tlds()

        assert isinstance(results, list)
        assert len(results) > 0


@pytest.mark.integration
class TestIntegrationErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_domain_format(self, skip_without_credentials):
        """Test checking invalid domain format."""
        client = GoDaddyClient()

        # This might raise an error or return invalid result
        # Depends on GoDaddy API behavior
        try:
            result = client.check("not a valid domain!!")
            # If it doesn't raise, it should at least return something
            assert "domain" in result or "error" in result
        except Exception as e:
            # Expected for invalid domains
            assert True

    def test_client_with_invalid_credentials(self):
        """Test client with invalid credentials."""
        client = GoDaddyClient(
            api_key="invalid_key",
            api_secret="invalid_secret"
        )

        # Should fail with authentication error
        with pytest.raises(Exception):  # Could be HTTPStatusError or similar
            client.check("example.com")


@pytest.mark.integration
@pytest.mark.slow
class TestIntegrationRetry:
    """Integration tests for retry logic (slow)."""

    def test_retry_logic_success(self, skip_without_credentials):
        """Test that retry logic works with real API."""
        # This test just verifies that the retry logic doesn't break normal requests
        client = GoDaddyClient(max_retries=3)
        result = client.check("example.com")

        assert "domain" in result
        assert "available" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
