"""
Form 4 XML Parser

Parses SEC Form 4 XML filings into structured trade data.
Form 4 reports insider transactions (buys, sells, options, etc.)
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

# Use lxml for better HTML/XML parsing (handles malformed XML)
try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Data validation constants
MAX_REASONABLE_TRADE_VALUE = Decimal("10000000000")  # $10 billion
MAX_REASONABLE_SHARES = Decimal("100000000")  # 100 million shares


class Form4Parser:
    """
    Parser for SEC Form 4 XML documents.

    Form 4 Structure:
    - reportingOwner: Insider information (name, relationship, etc.)
    - nonDerivativeTable: Stock transactions (buys/sells)
    - derivativeTable: Options/derivative transactions
    """

    @staticmethod
    def parse(xml_content: str) -> Dict[str, Any]:
        """
        Parse Form 4 XML into structured data.

        Args:
            xml_content: Raw XML content of Form 4

        Returns:
            Dictionary with insider info and transactions
        """
        try:
            # Try parsing with lxml XMLParser (preserves XML structure)
            if hasattr(ET, "XMLParser"):
                try:
                    # lxml is available - use XML parser with recovery mode
                    parser = ET.XMLParser(recover=True, encoding="utf-8")
                    root = ET.fromstring(xml_content.encode("utf-8"), parser)
                except Exception:
                    # Fallback to standard parsing
                    root = ET.fromstring(xml_content.encode("utf-8"))
            else:
                # Standard library xml.etree
                root = ET.fromstring(xml_content)
        except Exception as e:
            logger.error(f"Failed to parse Form 4 XML: {e}")
            raise ValueError(f"Invalid Form 4 XML: {e}")

        result = {
            "issuer": Form4Parser._parse_issuer(root),
            "reporting_owner": Form4Parser._parse_reporting_owner(root),
            "transactions": [],
        }

        # Parse non-derivative transactions (regular stock trades)
        non_derivative_txns = Form4Parser._parse_non_derivative_transactions(root)
        result["transactions"].extend(non_derivative_txns)

        # Parse derivative transactions (options, etc.)
        derivative_txns = Form4Parser._parse_derivative_transactions(root)
        result["transactions"].extend(derivative_txns)

        logger.info(
            f"Parsed Form 4: {result['reporting_owner'].get('name')} - "
            f"{len(result['transactions'])} transactions"
        )

        return result

    @staticmethod
    def _parse_issuer(root: ET.Element) -> Dict[str, str]:
        """Extract issuer (company) information."""
        issuer = root.find(".//issuer")
        if issuer is None:
            return {}

        cik = Form4Parser._get_text(issuer, ".//issuerCik", "")
        name = Form4Parser._get_text(issuer, ".//issuerName", "")
        ticker = Form4Parser._get_text(issuer, ".//issuerTradingSymbol", "")

        return {"cik": cik.zfill(10) if cik else "", "name": name, "ticker": ticker}

    @staticmethod
    def _parse_reporting_owner(root: ET.Element) -> Dict[str, Any]:
        """Extract reporting owner (insider) information."""
        owner = root.find(".//reportingOwner")
        if owner is None:
            return {}

        owner_id = owner.find(".//reportingOwnerId")
        relationship = owner.find(".//reportingOwnerRelationship")

        cik = Form4Parser._get_text(owner_id, ".//rptOwnerCik", "") if owner_id else ""
        name = (
            Form4Parser._get_text(owner_id, ".//rptOwnerName", "") if owner_id else ""
        )

        result = {
            "cik": cik.zfill(10) if cik else "",
            "name": name,
        }

        if relationship is not None:
            result["is_director"] = (
                Form4Parser._get_text(relationship, ".//isDirector") == "1"
            )
            result["is_officer"] = (
                Form4Parser._get_text(relationship, ".//isOfficer") == "1"
            )
            result["is_ten_percent_owner"] = (
                Form4Parser._get_text(relationship, ".//isTenPercentOwner") == "1"
            )
            result["is_other"] = (
                Form4Parser._get_text(relationship, ".//isOther") == "1"
            )
            result["officer_title"] = Form4Parser._get_text(
                relationship, ".//officerTitle"
            )
            result["other_text"] = Form4Parser._get_text(relationship, ".//otherText")

        return result

    @staticmethod
    def _parse_non_derivative_transactions(root: ET.Element) -> List[Dict[str, Any]]:
        """Parse non-derivative transactions (regular stock trades)."""
        transactions = []

        table = root.find(".//nonDerivativeTable")
        if table is None:
            return transactions

        for txn in table.findall("nonDerivativeTransaction"):
            try:
                parsed_txn = Form4Parser._parse_transaction(txn, is_derivative=False)
                if parsed_txn:
                    transactions.append(parsed_txn)
            except Exception as e:
                logger.warning(f"Failed to parse non-derivative transaction: {e}")
                continue

        return transactions

    @staticmethod
    def _parse_derivative_transactions(root: ET.Element) -> List[Dict[str, Any]]:
        """Parse derivative transactions (options, warrants, etc.)."""
        transactions = []

        table = root.find(".//derivativeTable")
        if table is None:
            return transactions

        for txn in table.findall("derivativeTransaction"):
            try:
                parsed_txn = Form4Parser._parse_transaction(txn, is_derivative=True)
                if parsed_txn:
                    transactions.append(parsed_txn)
            except Exception as e:
                logger.warning(f"Failed to parse derivative transaction: {e}")
                continue

        return transactions

    @staticmethod
    def _parse_transaction(
        txn: ET.Element, is_derivative: bool
    ) -> Optional[Dict[str, Any]]:
        """Parse a single transaction."""
        # Security title
        security_title = Form4Parser._get_text(txn, ".//securityTitle/value")

        # Transaction date
        txn_date_elem = txn.find(".//transactionDate")
        if txn_date_elem is None:
            return None

        txn_date_str = Form4Parser._get_text(txn_date_elem, "value")
        try:
            txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Invalid transaction date: {txn_date_str}")
            return None

        # Transaction coding
        coding = txn.find(".//transactionCoding")
        txn_code = Form4Parser._get_text(coding, "transactionCode") if coding else ""

        # Map transaction code to type
        # P = Purchase, S = Sale, A = Award, G = Gift, etc.
        txn_type = (
            "BUY" if txn_code in ["P", "A"] else "SELL" if txn_code == "S" else "OTHER"
        )

        # Transaction amounts
        amounts = txn.find(".//transactionAmounts")
        if amounts is None:
            return None

        shares_str = Form4Parser._get_text(amounts, "transactionShares/value", "0")
        price_str = Form4Parser._get_text(
            amounts, "transactionPricePerShare/value", "0"
        )
        acquired_disposed = Form4Parser._get_text(
            amounts, "transactionAcquiredDisposedCode/value"
        )

        try:
            shares = Decimal(shares_str) if shares_str else Decimal("0")
            price = Decimal(price_str) if price_str else Decimal("0")
        except (ValueError, TypeError):
            logger.warning(f"Invalid shares/price: {shares_str}/{price_str}")
            return None

        # Override transaction type based on acquired/disposed
        if acquired_disposed == "A":
            txn_type = "BUY"
        elif acquired_disposed == "D":
            txn_type = "SELL"

        # Calculate total value
        total_value = shares * price if shares and price else None

        # Data validation: Flag extreme values
        if total_value and total_value > MAX_REASONABLE_TRADE_VALUE:
            logger.warning(
                f"Extreme trade value detected: ${total_value:,.2f} "
                f"({shares:,.0f} shares @ ${price:,.2f}). "
                f"This may be a data error or unusual transaction."
            )
            # Skip trades over $10B - likely data errors
            return None

        if shares > MAX_REASONABLE_SHARES:
            logger.warning(
                f"Extreme share count detected: {shares:,.0f} shares. "
                f"This may be post-transaction holdings, not transaction amount. Skipping."
            )
            return None

        # Post-transaction shares owned
        post_txn_amounts = txn.find(".//postTransactionAmounts")
        shares_owned_str = (
            Form4Parser._get_text(
                post_txn_amounts, "sharesOwnedFollowingTransaction/value", "0"
            )
            if post_txn_amounts
            else "0"
        )

        try:
            shares_owned = (
                Decimal(shares_owned_str) if shares_owned_str else Decimal("0")
            )
        except (ValueError, TypeError):
            shares_owned = Decimal("0")

        # Ownership nature
        ownership = txn.find(".//ownershipNature")
        ownership_type = (
            Form4Parser._get_text(ownership, "directOrIndirectOwnership/value", "D")
            if ownership
            else "D"
        )
        ownership_type = "Direct" if ownership_type == "D" else "Indirect"

        return {
            "security_title": security_title,
            "transaction_date": txn_date,
            "transaction_code": txn_code,
            "transaction_type": txn_type,
            "shares": float(shares),
            "price_per_share": float(price) if price else None,
            "total_value": float(total_value) if total_value else None,
            "shares_owned_after": float(shares_owned),
            "ownership_type": ownership_type,
            "derivative_transaction": is_derivative,
        }

    @staticmethod
    def _get_text(element: Optional[ET.Element], path: str, default: str = "") -> str:
        """
        Safely extract text from XML element.

        Args:
            element: XML element to search
            path: XPath to find
            default: Default value if not found

        Returns:
            Element text or default
        """
        if element is None:
            return default

        found = (
            element.find(path)
            if "/" in path or "." in path
            else element.find(f".//{path}")
        )

        if found is not None and found.text:
            return found.text.strip()

        return default
