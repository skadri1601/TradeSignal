"""
SEC EDGAR API Client

Fetches insider trading Form 4 filings from SEC EDGAR database.
Implements rate limiting and best practices per SEC guidelines.
"""

import asyncio
import logging
from datetime import datetime, timedelta
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

        logger.info(f"SEC Client initialized with User-Agent: {self.user_agent}")

    async def _rate_limit(self):
        """Enforce rate limiting (max 10 req/sec)."""
        async with self._request_lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self._last_request_time

            if time_since_last < self.REQUEST_DELAY:
                await asyncio.sleep(self.REQUEST_DELAY - time_since_last)

            self._last_request_time = asyncio.get_event_loop().time()

    async def lookup_cik_by_ticker(self, ticker: str) -> Optional[str]:
        """
        Look up CIK for a ticker symbol using SEC company tickers JSON.

        Args:
            ticker: Stock ticker symbol

        Returns:
            CIK string or None if not found
        """
        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use SEC's company tickers JSON file
                url = "https://www.sec.gov/files/company_tickers.json"
                logger.info(f"Looking up CIK for ticker: {ticker}")
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

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

        # Note: Not using start_date filter to avoid issues with system clock
        # SEC will return most recent filings up to 'count' limit
        # if start_date:
        #     params["datea"] = start_date.strftime("%Y%m%d")

        url = f"{self.EDGAR_SEARCH_URL}?{urlencode(params)}"

        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching Form 4 filings from SEC: {url}")
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

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
            ns = {"atom": "http://www.w3.org/2005/Atom"}

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
        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, fetch the index page to find the XML document link
                logger.debug(f"Fetching filing index: {filing_url}")
                response = await client.get(filing_url, headers=self.headers)
                response.raise_for_status()

                # Parse HTML to find the primary Form 4 XML document
                html_content = response.text

                import re

                # Pattern: find XML files in href attributes
                # The raw XML file is in the root directory (not in xslF345X05/ subfolder)
                # Format: href="/Archives/edgar/data/CIK/ACCESSION/filename.xml"
                xml_pattern = r'href="(/Archives/edgar/data/[^"]+\.xml)"'
                all_matches = re.findall(xml_pattern, html_content)

                # Filter: get raw XML (NOT in xslF345X subfolder)
                # The raw XML has no path prefix, styled one has "xslF345X05/" prefix
                xml_matches = [m for m in all_matches if "/xslF345X" not in m]

                if not xml_matches:
                    logger.error(f"No raw XML document found in filing: {filing_url}")
                    logger.debug(f"All XML files found: {all_matches}")
                    raise ValueError("No raw XML document found in filing")

                # Get the first raw XML file (full path from SEC root)
                xml_path = xml_matches[0]

                # xml_path already starts with /Archives, so just prepend base URL
                xml_url = f"{self.BASE_URL}{xml_path}"

                logger.info(f"Fetching XML document: {xml_url}")

                await self._rate_limit()

                # Fetch the actual XML document
                xml_response = await client.get(xml_url, headers=self.headers)
                xml_response.raise_for_status()

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

        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.text)

                ns = {"atom": "http://www.w3.org/2005/Atom"}
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
