"""
SEC EDGAR API Client

Fetches insider trading Form 4 filings from SEC EDGAR database.
Implements rate limiting and best practices per SEC guidelines.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class SECClient:
    """
    Client for interacting with SEC EDGAR API.

    SEC Guidelines:
    - Rate limit: Max 10 requests per second
    - User-Agent header required: Name + Email
    - Be respectful of SEC resources
    """

    BASE_URL = "https://www.sec.gov"
    EDGAR_SEARCH_URL = f"{BASE_URL}/cgi-bin/browse-edgar"
    
    # XML namespace URI for ATOM feeds (not an HTTP connection - this is an XML namespace identifier)
    # Note: XML namespaces use http:// URIs by convention, but these are identifiers, not actual URLs
    ATOM_NAMESPACE_URI = "http://www.w3.org/2005/Atom"

    # Rate limiting: 10 requests per second max
    MAX_REQUESTS_PER_SECOND = 10
    REQUEST_DELAY = 1.0 / MAX_REQUESTS_PER_SECOND

    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize SEC client.

        Args:
            user_agent: Custom user agent (must include name and email)
        """
        self.user_agent = user_agent or settings.sec_user_agent
        if not self.user_agent or "@" not in self.user_agent:
            raise ValueError(
                "SEC requires User-Agent with contact email. "
                "Set SEC_USER_AGENT in .env (e.g., 'Your Name your@email.com')"
            )

        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }

        self._last_request_time = 0.0
        self._request_lock = asyncio.Lock()
        
        # Timeout configuration: separate connect and read timeouts
        self.timeout = httpx.Timeout(
            connect=10.0,  # 10 seconds to establish connection
            read=settings.sec_api_timeout_seconds,  # Configurable read timeout
            write=10.0,  # 10 seconds to write request
            pool=10.0,  # 10 seconds to get connection from pool
        )
        self.max_retries = settings.sec_api_max_retries

        logger.info(
            f"SEC Client initialized with User-Agent: {self.user_agent}, "
            f"timeout: {settings.sec_api_timeout_seconds}s, max_retries: {self.max_retries}"
        )

    async def _rate_limit(self):
        """Enforce rate limiting (max 10 req/sec)."""
        async with self._request_lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self._last_request_time

            if time_since_last < self.REQUEST_DELAY:
                await asyncio.sleep(self.REQUEST_DELAY - time_since_last)

            self._last_request_time = asyncio.get_event_loop().time()
    
    async def _make_http_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make a single HTTP request.
        
        Args:
            client: httpx AsyncClient instance
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to httpx client
            
        Returns:
            httpx.Response object
            
        Raises:
            ValueError: If HTTP method is unsupported
            httpx.HTTPError: If request fails
        """
        method_upper = method.upper()
        if method_upper == "GET":
            response = await client.get(url, headers=self.headers, **kwargs)
        elif method_upper == "POST":
            response = await client.post(url, headers=self.headers, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response

    async def _handle_timeout_error(
        self,
        e: Exception,
        attempt: int,
        url: str
    ) -> None:
        """
        Handle timeout errors with retry logic.
        
        Args:
            e: The timeout exception
            attempt: Current attempt number (0-indexed)
            url: Request URL for logging
            
        Raises:
            The timeout exception if max retries exceeded
        """
        timeout_type = type(e).__name__
        
        if attempt < self.max_retries - 1:
            # Exponential backoff: 2^attempt seconds
            wait_time = 2 ** attempt
            logger.warning(
                f"SEC API {timeout_type} (attempt {attempt + 1}/{self.max_retries}) "
                f"for {url} (timeout: {self.timeout.read}s). "
                f"Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
        else:
            logger.error(
                f"SEC API request failed after {self.max_retries} attempts "
                f"(last error: {timeout_type}) for {url}: {e}"
            )
            raise

    def _handle_http_error(self, e: httpx.HTTPError, url: str) -> None:
        """
        Handle non-retryable HTTP errors.
        
        Args:
            e: The HTTP error exception
            url: Request URL for logging
            
        Raises:
            The HTTP error exception
        """
        error_type = type(e).__name__
        logger.error(
            f"SEC API HTTP error (non-retryable, {error_type}) for {url}: {e}"
        )
        raise

    async def _request_with_retry(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic for timeout errors.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to httpx client
            
        Returns:
            httpx.Response object
            
        Raises:
            httpx.HTTPError: If all retries fail
        """
        logger.debug(
            f"SEC API request: {method} {url} "
            f"(timeout: {self.timeout.read}s, max_retries: {self.max_retries})"
        )
        
        for attempt in range(self.max_retries):
            try:
                await self._rate_limit()
                logger.debug(f"SEC API request attempt {attempt + 1}/{self.max_retries} for {url}")
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await self._make_http_request(client, method, url, **kwargs)
                    
                    if attempt > 0:
                        logger.info(
                            f"SEC API request succeeded on attempt {attempt + 1}/{self.max_retries} for {url}"
                        )
                    return response
                    
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.PoolTimeout) as e:
                await self._handle_timeout_error(e, attempt, url)
            except httpx.HTTPError as e:
                self._handle_http_error(e, url)
            except Exception as e:
                # Catch any other unexpected exceptions
                error_type = type(e).__name__
                logger.error(
                    f"SEC API unexpected error ({error_type}) for {url}: {e}",
                    exc_info=True
                )
                raise
        
        # Should never reach here, but just in case
        raise httpx.HTTPError("Request failed after retries")

    async def lookup_cik_by_ticker(self, ticker: str) -> Optional[str]:
        """
        Look up CIK for a ticker symbol using SEC company tickers JSON.

        Args:
            ticker: Stock ticker symbol

        Returns:
            CIK string or None if not found
        """
        try:
            # Use SEC's company tickers JSON file
            url = "https://www.sec.gov/files/company_tickers.json"
            logger.info(f"Looking up CIK for ticker: {ticker}")
            response = await self._request_with_retry("GET", url)

            data = response.json()
            ticker_upper = ticker.upper()

            # Search for ticker in the JSON data
            for item in data.values():
                if item.get("ticker", "").upper() == ticker_upper:
                    cik = str(item.get("cik_str", "")).zfill(10)  # Pad with zeros
                    logger.info(f"Found CIK {cik} for ticker {ticker}")
                    return cik

            logger.warning(f"No CIK found for ticker: {ticker}")
            return None

        except Exception as e:
            logger.error(f"CIK lookup failed for {ticker}: {e}")
            return None

    async def fetch_recent_form4_filings(
        self,
        cik: Optional[str] = None,
        ticker: Optional[str] = None,
        start_date: Optional[datetime] = None,
        count: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent Form 4 filings from SEC EDGAR.

        Args:
            cik: Company CIK (Central Index Key)
            ticker: Company ticker symbol
            start_date: Fetch filings after this date
            count: Maximum number of filings to fetch

        Returns:
            List of filing metadata dictionaries
        """
        if not cik and not ticker:
            raise ValueError("Must provide either CIK or ticker")

        # If ticker provided without CIK, look up the CIK first
        if ticker and not cik:
            cik = await self.lookup_cik_by_ticker(ticker)
            if not cik:
                logger.warning(
                    f"Could not find CIK for ticker {ticker}, search may return no results"
                )

        params = {
            "action": "getcompany",
            "type": "4",  # Form 4 filings
            "dateb": "",  # End date (empty = today)
            "owner": "include",
            "output": "atom",  # Get results in ATOM feed format
            "count": min(count, 100),  # SEC max is 100
        }

        if cik:
            params["CIK"] = cik.lstrip("0")  # Remove leading zeros
        elif ticker:
            params["company"] = ticker

        # Optional: Filter filings by start date to reduce unnecessary API calls
        # SEC will return most recent filings up to 'count' limit
        if start_date:
            params["datea"] = start_date.strftime("%Y%m%d")

        url = f"{self.EDGAR_SEARCH_URL}?{urlencode(params)}"

        try:
            logger.info(f"Fetching Form 4 filings from SEC: {url}")
            response = await self._request_with_retry("GET", url)

            # Parse ATOM feed
            filings = self._parse_atom_feed(response.text)
            logger.info(f"Found {len(filings)} Form 4 filings")

            return filings

        except httpx.HTTPError as e:
            logger.error(f"SEC API request failed: {e}")
            raise

    def _parse_atom_feed(self, atom_xml: str) -> List[Dict[str, Any]]:
        """
        Parse SEC ATOM feed XML.

        Args:
            atom_xml: ATOM feed XML string

        Returns:
            List of filing metadata
        """
        import xml.etree.ElementTree as ET

        filings = []

        try:
            root = ET.fromstring(atom_xml)

            # ATOM namespace
            ns = {"atom": self.ATOM_NAMESPACE_URI}

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                link = entry.find("atom:link", ns)
                updated = entry.find("atom:updated", ns)

                filing = {
                    "title": title.text if title is not None else "",
                    "filing_url": link.get("href") if link is not None else "",
                    "filing_date": updated.text if updated is not None else "",
                }

                # Extract accession number from URL
                if filing["filing_url"]:
                    # URL format: .../Archives/edgar/data/CIK/ACCESSION/filename.xml
                    parts = filing["filing_url"].split("/")
                    if len(parts) >= 3:
                        filing["accession_number"] = parts[-2].replace("-", "")

                filings.append(filing)

        except ET.ParseError as e:
            logger.error(f"Failed to parse ATOM feed: {e}")
            return []

        return filings

    async def fetch_form4_document(self, filing_url: str) -> str:
        """
        Fetch the actual Form 4 XML document.

        Args:
            filing_url: URL to the Form 4 filing page (HTML index)

        Returns:
            Raw XML content of Form 4
        """
        try:
            # First, fetch the index page to find the XML document link
            logger.debug(f"Fetching filing index: {filing_url}")
            response = await self._request_with_retry("GET", filing_url)

            # Parse HTML to find the primary Form 4 XML document
            html_content = response.text

            import re

            # Pattern: find XML files in href attributes
            # The raw XML file is in the root directory (not in xslF345X05/ subfolder)
            # Format: href="/Archives/edgar/data/CIK/ACCESSION/filename.xml"
            xml_pattern = r'href="(/Archives/edgar/data/[^"]+\.xml)"'
            all_matches = re.findall(xml_pattern, html_content)

            # Filter: get raw Form 4 XML (NOT in xslF345X subfolder, NOT exfilingfees)
            # Priority: form4.xml > wf-form4.xml > doc4.xml
            # Exclude: exfilingfees_htm.xml (not a Form 4), styled versions (xslF345X)
            xml_matches = [
                m for m in all_matches
                if "/xslF345X" not in m and "exfilingfees" not in m.lower()
            ]

            # Prioritize files named "form4.xml"
            form4_files = [m for m in xml_matches if "form4.xml" in m.lower()]
            if form4_files:
                xml_matches = form4_files

            if not xml_matches:
                logger.error(f"No raw XML document found in filing: {filing_url}")
                logger.debug(f"All XML files found: {all_matches}")
                raise ValueError("No raw XML document found in filing")

            # Get the first raw XML file (full path from SEC root)
            xml_path = xml_matches[0]

            # xml_path already starts with /Archives, so just prepend base URL
            xml_url = f"{self.BASE_URL}{xml_path}"

            logger.info(f"Fetching XML document: {xml_url}")

            # Fetch the actual XML document
            xml_response = await self._request_with_retry("GET", xml_url)

            return xml_response.text

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch Form 4 document: {e}")
            raise

    async def search_company_by_ticker(self, ticker: str) -> Optional[Dict[str, str]]:
        """
        Search for company information by ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Company info (CIK, name) or None if not found
        """
        params = {
            "action": "getcompany",
            "company": ticker,
            "output": "atom",
            "count": 1,
        }

        url = f"{self.EDGAR_SEARCH_URL}?{urlencode(params)}"

        try:
            response = await self._request_with_retry("GET", url)

            import xml.etree.ElementTree as ET

            root = ET.fromstring(response.text)

            ns = {"atom": self.ATOM_NAMESPACE_URI}
            entry = root.find("atom:entry", ns)

            if entry is None:
                return None

            title = entry.find("atom:title", ns)

            # Title format: "CIK (TICKER) - Company Name"
            if title is not None and title.text:
                parts = title.text.split(" - ")
                if len(parts) >= 2:
                    cik_ticker = parts[0].strip()
                    name = parts[1].strip()

                    # Extract CIK
                    cik = cik_ticker.split()[0].strip()

                    return {
                        "cik": cik.zfill(10),  # Pad to 10 digits
                        "name": name,
                        "ticker": ticker.upper(),
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to search company: {e}")
            return None
