"""
Unit tests for DNS resolver utility.

Tests DNS resolution, caching, fallback logic, and error handling.
"""

import pytest
import socket
import time
from unittest.mock import patch, Mock
from app.utils.dns_resolver import (
    resolve_hostname,
    resolve_database_url,
    clear_dns_cache,
    get_dns_cache_stats,
    DNSResolutionError,
    _get_cached_ip,
    _cache_ip,
)


class TestDNSResolver:
    """Test suite for DNS resolver functionality."""

    def setup_method(self):
        """Clear DNS cache before each test."""
        clear_dns_cache()

    def test_resolve_hostname_success(self):
        """Test successful DNS resolution."""
        # Resolve a known hostname
        ip = resolve_hostname("google.com", use_cache=False)

        # Should return a valid IP address
        assert ip is not None
        # Verify it's a valid IPv4 address
        socket.inet_aton(ip)  # Raises OSError if invalid

    def test_resolve_hostname_with_caching(self):
        """Test DNS resolution uses cache on second call."""
        hostname = "google.com"

        # First call - should hit DNS
        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            mock_dns.return_value = "8.8.8.8"

            ip1 = resolve_hostname(hostname, cache_ttl=300)
            assert ip1 == "8.8.8.8"
            assert mock_dns.call_count == 1

        # Second call - should use cache
        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            ip2 = resolve_hostname(hostname, cache_ttl=300)
            assert ip2 == "8.8.8.8"
            assert mock_dns.call_count == 0  # Should not call DNS again

    def test_resolve_hostname_cache_expiration(self):
        """Test that cache expires after TTL."""
        hostname = "example.com"

        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            mock_dns.return_value = "1.2.3.4"

            # First call with very short TTL
            ip1 = resolve_hostname(hostname, cache_ttl=1)
            assert ip1 == "1.2.3.4"
            assert mock_dns.call_count == 1

            # Wait for cache to expire
            time.sleep(1.5)

            # Second call should hit DNS again
            mock_dns.reset_mock()
            ip2 = resolve_hostname(hostname, cache_ttl=1)
            assert ip2 == "1.2.3.4"
            assert mock_dns.call_count == 1  # Should call DNS again

    def test_resolve_hostname_invalid_hostname(self):
        """Test DNS resolution with invalid hostname."""
        with pytest.raises(DNSResolutionError):
            resolve_hostname("this-hostname-definitely-does-not-exist-12345.invalid", max_retries=1, use_cache=False)

    def test_resolve_hostname_uses_expired_cache_on_failure(self):
        """Test that expired cache is used as last resort when DNS fails."""
        hostname = "example.com"

        # Cache an IP with very short TTL
        _cache_ip(hostname, "5.6.7.8", ttl=1)

        # Wait for cache to expire
        time.sleep(1.5)

        # Mock DNS to fail
        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            mock_dns.side_effect = socket.gaierror("DNS failed")

            # Should fall back to expired cache
            ip = resolve_hostname(hostname, max_retries=1)
            assert ip == "5.6.7.8"

    def test_resolve_hostname_retry_logic(self):
        """Test that DNS resolution retries on failure."""
        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            with patch('time.sleep'):  # Mock sleep to speed up test
                # Fail twice, succeed on third attempt
                mock_dns.side_effect = [
                    socket.gaierror("Attempt 1 failed"),
                    socket.gaierror("Attempt 2 failed"),
                    "9.10.11.12"
                ]

                ip = resolve_hostname("retry-test.com", max_retries=3, use_cache=False)
                assert ip == "9.10.11.12"
                assert mock_dns.call_count == 3

    def test_resolve_database_url_success(self):
        """Test resolving database URL."""
        original_url = "postgresql://user:pass@google.com:5432/dbname"

        with patch('app.utils.dns_resolver.resolve_hostname') as mock_resolve:
            mock_resolve.return_value = "142.250.185.46"

            resolved_url = resolve_database_url(original_url)

            # Should replace hostname with IP
            assert "142.250.185.46" in resolved_url
            assert "google.com" not in resolved_url
            # Should preserve other components
            assert "user:pass" in resolved_url
            assert ":5432" in resolved_url
            assert "/dbname" in resolved_url

    def test_resolve_database_url_already_ip(self):
        """Test that URL with IP address is not modified."""
        original_url = "postgresql://user:pass@127.0.0.1:5432/dbname"

        # Should return unchanged
        resolved_url = resolve_database_url(original_url)
        assert resolved_url == original_url

    def test_resolve_database_url_no_hostname(self):
        """Test error handling for URL without hostname."""
        with pytest.raises(ValueError, match="does not contain a hostname"):
            resolve_database_url("postgresql:///dbname")

    def test_clear_dns_cache(self):
        """Test clearing DNS cache."""
        # Add some entries to cache
        _cache_ip("host1.com", "1.1.1.1", 300)
        _cache_ip("host2.com", "2.2.2.2", 300)

        stats = get_dns_cache_stats()
        assert stats["total_entries"] == 2

        # Clear cache
        clear_dns_cache()

        stats = get_dns_cache_stats()
        assert stats["total_entries"] == 0

    def test_get_dns_cache_stats(self):
        """Test DNS cache statistics."""
        # Add fresh entry
        _cache_ip("fresh.com", "1.1.1.1", 300)

        # Add entry that will expire
        _cache_ip("stale.com", "2.2.2.2", 1)
        time.sleep(1.5)

        stats = get_dns_cache_stats()

        assert stats["total_entries"] == 2
        assert stats["fresh_entries"] == 1
        assert stats["expired_entries"] == 1

        # Check entries details
        assert len(stats["entries"]) == 2

        fresh_entry = next(e for e in stats["entries"] if e["hostname"] == "fresh.com")
        assert fresh_entry["is_fresh"] is True
        assert fresh_entry["ttl_remaining"] > 0

        stale_entry = next(e for e in stats["entries"] if e["hostname"] == "stale.com")
        assert stale_entry["is_fresh"] is False
        assert stale_entry["ttl_remaining"] == 0

    def test_resolve_supabase_url(self):
        """Test resolving a Supabase-like database URL."""
        supabase_url = "postgresql://postgres:password@db.fcxqcofopmnbdnqdsirs.supabase.co:5432/postgres"

        with patch('app.utils.dns_resolver.resolve_hostname') as mock_resolve:
            mock_resolve.return_value = "54.176.87.226"

            resolved_url = resolve_database_url(supabase_url)

            # Verify hostname was resolved
            mock_resolve.assert_called_once_with("db.fcxqcofopmnbdnqdsirs.supabase.co", cache_ttl=300)

            # Verify URL structure
            assert "54.176.87.226" in resolved_url
            assert "db.fcxqcofopmnbdnqdsirs.supabase.co" not in resolved_url
            assert "postgres:password" in resolved_url
            assert ":5432" in resolved_url
            assert "/postgres" in resolved_url

    def test_concurrent_cache_access(self):
        """Test that cache handles concurrent access."""
        hostname = "concurrent-test.com"

        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            mock_dns.return_value = "10.0.0.1"

            # Multiple calls in quick succession
            results = [resolve_hostname(hostname) for _ in range(10)]

            # All should return same IP
            assert all(ip == "10.0.0.1" for ip in results)

            # DNS should only be called once (rest use cache)
            assert mock_dns.call_count == 1


class TestCacheManagement:
    """Test cache-specific functionality."""

    def setup_method(self):
        """Clear DNS cache before each test."""
        clear_dns_cache()

    def test_cache_ip_and_get_cached_ip(self):
        """Test caching and retrieving IP."""
        _cache_ip("test.com", "1.2.3.4", 300)

        cached_ip = _get_cached_ip("test.com")
        assert cached_ip == "1.2.3.4"

    def test_get_cached_ip_not_found(self):
        """Test retrieving non-existent cache entry."""
        cached_ip = _get_cached_ip("nonexistent.com")
        assert cached_ip is None

    def test_get_cached_ip_expired(self):
        """Test retrieving expired cache entry."""
        _cache_ip("expired.com", "5.6.7.8", 1)
        time.sleep(1.5)

        cached_ip = _get_cached_ip("expired.com")
        assert cached_ip is None  # Should be None (cache cleaned up)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Clear DNS cache before each test."""
        clear_dns_cache()

    def test_resolve_hostname_with_no_cache(self):
        """Test resolution with caching disabled."""
        with patch('app.utils.dns_resolver._resolve_with_system_dns') as mock_dns:
            mock_dns.return_value = "11.12.13.14"

            # First call with caching disabled
            ip1 = resolve_hostname("nocache.com", use_cache=False)
            assert ip1 == "11.12.13.14"

            # Second call should hit DNS again
            mock_dns.reset_mock()
            ip2 = resolve_hostname("nocache.com", use_cache=False)
            assert ip2 == "11.12.13.14"
            assert mock_dns.call_count == 1

    def test_resolve_empty_hostname(self):
        """Test error handling for empty hostname."""
        with pytest.raises(Exception):
            resolve_database_url("postgresql://user:pass@:5432/db")

    def test_malformed_url(self):
        """Test error handling for malformed URL."""
        with pytest.raises(Exception):
            resolve_database_url("not-a-valid-url")
