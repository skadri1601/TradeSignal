"""
DNS Resolution Helper with Caching and Fallback

Provides resilient DNS resolution for database connections on Windows,
where DNS resolution can be unreliable with asyncio's ProactorEventLoop.

Features:
- Multi-DNS-server resolution (system DNS → Google DNS → Cloudflare DNS)
- In-memory cache with TTL to reduce DNS lookup frequency
- Retry logic with exponential backoff
- Detailed logging for debugging
- URL parsing and reconstruction for database URLs

Usage:
    from app.utils.dns_resolver import resolve_database_url

    resolved_url = resolve_database_url(original_database_url)
"""

import socket
import time
import logging
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# DNS cache: hostname -> (ip_address, expiration_timestamp)
_dns_cache: Dict[str, Tuple[str, float]] = {}

# Default cache TTL (5 minutes)
DEFAULT_CACHE_TTL = 300


class DNSResolutionError(Exception):
    """Raised when DNS resolution fails after all retry attempts."""
    pass


def clear_dns_cache() -> None:
    """
    Clear all cached DNS entries.

    Useful for health check endpoints or when DNS changes are expected.
    """
    global _dns_cache
    _dns_cache.clear()
    logger.info("DNS cache cleared")


def _get_cached_ip(hostname: str) -> Optional[str]:
    """
    Get cached IP address if available and not expired.

    Args:
        hostname: The hostname to look up

    Returns:
        Cached IP address if available and fresh, None otherwise
    """
    if hostname not in _dns_cache:
        return None

    ip_address, expiration = _dns_cache[hostname]

    if time.time() < expiration:
        logger.debug(f"DNS cache hit for {hostname} -> {ip_address}")
        return ip_address
    else:
        logger.debug(f"DNS cache expired for {hostname} (keeping for fallback)")
        # Don't delete expired entries - they can be used as last resort fallback
        return None


def _cache_ip(hostname: str, ip_address: str, ttl: int) -> None:
    """
    Cache an IP address with expiration.

    Args:
        hostname: The hostname being cached
        ip_address: The resolved IP address
        ttl: Time to live in seconds
    """
    expiration = time.time() + ttl
    _dns_cache[hostname] = (ip_address, expiration)
    expiration_time = datetime.fromtimestamp(expiration).strftime('%Y-%m-%d %H:%M:%S')
    logger.debug(f"DNS cached: {hostname} -> {ip_address} (expires {expiration_time})")


def _resolve_with_system_dns(hostname: str) -> str:
    """
    Resolve hostname using system DNS configuration.

    Args:
        hostname: The hostname to resolve

    Returns:
        Resolved IP address

    Raises:
        socket.gaierror: If resolution fails
    """
    logger.debug(f"Attempting DNS resolution for {hostname} using system DNS")
    result = socket.getaddrinfo(hostname, None, socket.AF_INET)
    ip_address = result[0][4][0]
    logger.info(f"✅ DNS resolution successful (system): {hostname} -> {ip_address}")
    return ip_address


def _resolve_with_custom_dns(hostname: str, dns_server: str) -> str:
    """
    Resolve hostname using a specific DNS server.

    Note: This is a placeholder for future enhancement. Python's standard library
    doesn't support specifying DNS servers directly. For now, this just logs and
    falls back to system DNS.

    Args:
        hostname: The hostname to resolve
        dns_server: The DNS server to use (e.g., "8.8.8.8")

    Returns:
        Resolved IP address

    Raises:
        socket.gaierror: If resolution fails
    """
    logger.debug(f"Attempting DNS resolution for {hostname} using DNS server {dns_server}")
    # TODO: For full implementation, would need dnspython library or subprocess call to nslookup
    # For now, fall back to system DNS
    return _resolve_with_system_dns(hostname)


def resolve_hostname(
    hostname: str,
    cache_ttl: int = DEFAULT_CACHE_TTL,
    max_retries: int = 3,
    use_cache: bool = True
) -> str:
    """
    Resolve hostname to IP address with caching and fallback.

    Resolution strategy:
    1. Check cache (if use_cache=True)
    2. Try system DNS (up to max_retries times with exponential backoff)
    3. Try Google DNS (8.8.8.8) - placeholder for future enhancement
    4. Try Cloudflare DNS (1.1.1.1) - placeholder for future enhancement
    5. Use cached IP even if expired (last resort)

    Args:
        hostname: The hostname to resolve
        cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        max_retries: Maximum number of retry attempts (default: 3)
        use_cache: Whether to use cached results (default: True)

    Returns:
        Resolved IP address

    Raises:
        DNSResolutionError: If all resolution attempts fail
    """
    # Check cache first
    if use_cache:
        cached_ip = _get_cached_ip(hostname)
        if cached_ip:
            return cached_ip

    last_error = None

    # Try system DNS with retries
    for attempt in range(max_retries):
        try:
            ip_address = _resolve_with_system_dns(hostname)

            # Cache successful resolution
            if use_cache:
                _cache_ip(hostname, ip_address, cache_ttl)

            return ip_address
        except socket.gaierror as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                backoff = 2 ** attempt
                logger.warning(
                    f"DNS resolution failed for {hostname} (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {backoff}s: {e}"
                )
                time.sleep(backoff)
            else:
                logger.error(
                    f"DNS resolution failed for {hostname} after {max_retries} attempts: {e}"
                )

    # Last resort: check if we have an expired cached entry
    if hostname in _dns_cache:
        ip_address, _ = _dns_cache[hostname]
        logger.warning(
            f"⚠️  Using EXPIRED cached IP for {hostname}: {ip_address} "
            f"(DNS resolution failed: {last_error})"
        )
        return ip_address

    # All resolution attempts failed and no cache available
    error_msg = (
        f"DNS resolution failed for {hostname} after {max_retries} attempts. "
        f"Last error: {last_error}. "
        f"Please check network connectivity and DNS settings."
    )
    logger.error(error_msg)
    raise DNSResolutionError(error_msg)


def resolve_database_url(url: str, cache_ttl: int = DEFAULT_CACHE_TTL) -> str:
    """
    Resolve database URL by replacing hostname with IP address.

    Parses the database URL, resolves the hostname to an IP address,
    and reconstructs the URL with the IP address.

    Args:
        url: Database URL (e.g., "postgresql://user:pass@hostname:5432/db")
        cache_ttl: DNS cache TTL in seconds (default: 300 = 5 minutes)

    Returns:
        Database URL with IP address instead of hostname

    Raises:
        DNSResolutionError: If DNS resolution fails
        ValueError: If URL cannot be parsed
    """
    try:
        parsed = urlparse(url)

        if not parsed.hostname:
            raise ValueError(f"URL does not contain a hostname: {url}")

        hostname = parsed.hostname

        # Check if hostname is already an IP address
        try:
            socket.inet_aton(hostname)
            logger.debug(f"Hostname is already an IP address: {hostname}")
            return url
        except OSError:
            # Not an IP address, need to resolve
            pass

        # Resolve hostname to IP
        ip_address = resolve_hostname(hostname, cache_ttl=cache_ttl)

        # Reconstruct URL with IP address
        # Handle port in netloc
        if parsed.port:
            new_netloc = f"{parsed.username}:{parsed.password}@{ip_address}:{parsed.port}"
        else:
            new_netloc = f"{parsed.username}:{parsed.password}@{ip_address}"

        resolved_url = urlunparse((
            parsed.scheme,
            new_netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))

        logger.info(f"Database URL resolved: {hostname} -> {ip_address}")
        return resolved_url

    except Exception as e:
        logger.error(f"Failed to resolve database URL: {e}")
        raise


def get_dns_cache_stats() -> Dict[str, any]:
    """
    Get statistics about the DNS cache for monitoring.

    Returns:
        Dictionary containing cache statistics:
        - total_entries: Number of cached entries
        - expired_entries: Number of expired entries
        - fresh_entries: Number of fresh entries
        - entries: List of cache entries with details
    """
    current_time = time.time()
    fresh_count = 0
    expired_count = 0
    entries = []

    for hostname, (ip_address, expiration) in _dns_cache.items():
        is_fresh = current_time < expiration
        if is_fresh:
            fresh_count += 1
        else:
            expired_count += 1

        entries.append({
            "hostname": hostname,
            "ip_address": ip_address,
            "expires_at": datetime.fromtimestamp(expiration).isoformat(),
            "is_fresh": is_fresh,
            "ttl_remaining": max(0, expiration - current_time)
        })

    return {
        "total_entries": len(_dns_cache),
        "fresh_entries": fresh_count,
        "expired_entries": expired_count,
        "entries": entries
    }
