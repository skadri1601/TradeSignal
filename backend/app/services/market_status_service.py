"""
Market Status Service

Detects if US stock market is currently open using pandas-market-calendars (FREE).
Based on TRUTH_FREE.md Phase 3.4 specifications.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import pytz
import pandas_market_calendars as mcal
import logging

logger = logging.getLogger(__name__)


class MarketStatusService:
    """Check if US stock market is currently open (FREE)"""

    _nyse_calendar = None

    @classmethod
    def _get_nyse_calendar(cls):
        """Get or create NYSE calendar instance"""
        if cls._nyse_calendar is None:
            cls._nyse_calendar = mcal.get_calendar("NYSE")
        return cls._nyse_calendar

    @classmethod
    def is_market_open(cls) -> Dict[str, Any]:
        """
        Check if US stock market is currently open.

        Returns:
            dict: Market status information including:
                - is_open: bool - Whether market is currently open
                - status: str - 'open' or 'closed'
                - reason: str - Reason for current status
                - next_open: str - When market opens next (if closed)
                - closes_at: str - When market closes (if open)
                - time_until_close: str - Time remaining until close (if open)
        """
        ny_tz = pytz.timezone("America/New_York")
        now = datetime.now(ny_tz)

        try:
            nyse = cls._get_nyse_calendar()

            # Check if today is a trading day
            schedule = nyse.schedule(start_date=now.date(), end_date=now.date())

            if schedule.empty:
                # Market closed (weekend or holiday)
                next_open = cls._get_next_open_time(nyse, now)
                return {
                    "is_open": False,
                    "status": "closed",
                    "reason": "Weekend or Market Holiday",
                    "next_open": next_open,
                    "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
                }

            # Check if within market hours
            # pandas-market-calendars returns times in UTC, convert to ET
            market_open_utc = schedule.iloc[0]["market_open"].to_pydatetime()
            market_close_utc = schedule.iloc[0]["market_close"].to_pydatetime()

            # Convert to ET timezone
            if market_open_utc.tzinfo is None:
                market_open_utc = pytz.UTC.localize(market_open_utc)
            if market_close_utc.tzinfo is None:
                market_close_utc = pytz.UTC.localize(market_close_utc)

            market_open = market_open_utc.astimezone(ny_tz)
            market_close = market_close_utc.astimezone(ny_tz)

            if market_open <= now <= market_close:
                time_until_close = market_close - now
                hours, remainder = divmod(time_until_close.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)

                return {
                    "is_open": True,
                    "status": "open",
                    "reason": "Regular Trading Hours",
                    "closes_at": market_close.strftime("%I:%M %p ET"),
                    "time_until_close": f"{int(hours)}h {int(minutes)}m",
                    "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
                }

            # Market is closed (before or after hours)
            if now < market_open:
                reason = "Pre-Market (Before Opening)"
                next_open_str = market_open.strftime("%I:%M %p ET today")
            else:
                reason = "After Market Close"
                next_open_str = cls._get_next_open_time(nyse, now)

            return {
                "is_open": False,
                "status": "closed",
                "reason": reason,
                "next_open": next_open_str,
                "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
            }

        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            # Fallback: simple time-based check
            return cls._fallback_market_check(now)

    @classmethod
    def _get_next_open_time(cls, nyse_calendar, current_time) -> str:
        """
        Get next market open time.

        Args:
            nyse_calendar: NYSE calendar instance
            current_time: Current datetime in ET timezone

        Returns:
            str: Formatted next open time
        """
        try:
            # Look ahead 7 days to find next open
            schedule = nyse_calendar.schedule(
                start_date=current_time.date(),
                end_date=current_time.date() + timedelta(days=7),
            )

            for idx, row in schedule.iterrows():
                market_open_time_utc = row["market_open"].to_pydatetime()
                # Convert to ET timezone
                if market_open_time_utc.tzinfo is None:
                    market_open_time_utc = pytz.UTC.localize(market_open_time_utc)
                market_open_time = market_open_time_utc.astimezone(
                    pytz.timezone("America/New_York")
                )
                if market_open_time > current_time:
                    return market_open_time.strftime("%A, %B %d at %I:%M %p ET")

            return "Unknown (check again later)"

        except Exception as e:
            logger.error(f"Error getting next open time: {e}")
            return "Unknown"

    @classmethod
    def _fallback_market_check(cls, now: datetime) -> Dict[str, Any]:
        """
        Fallback market check using simple time-based logic.
        Used when pandas-market-calendars fails.

        Args:
            now: Current datetime in ET timezone

        Returns:
            dict: Basic market status
        """
        # Weekday check (0=Monday, 6=Sunday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return {
                "is_open": False,
                "status": "closed",
                "reason": "Weekend",
                "next_open": "Monday at 9:30 AM ET",
                "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
                "fallback_mode": True,
            }

        # Time check (9:30 AM - 4:00 PM ET)
        market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

        if market_open_time <= now <= market_close_time:
            return {
                "is_open": True,
                "status": "open",
                "reason": "Regular Trading Hours (Fallback Mode)",
                "closes_at": "4:00 PM ET",
                "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
                "fallback_mode": True,
            }

        return {
            "is_open": False,
            "status": "closed",
            "reason": "Outside Market Hours (Fallback Mode)",
            "next_open": "9:30 AM ET",
            "current_time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
            "fallback_mode": True,
        }

    @classmethod
    def should_refresh_aggressively(cls) -> bool:
        """
        Determine if we should refresh data more frequently.
        Returns True if market is open, False otherwise.

        This can be used to adjust refresh intervals:
        - Market open: refresh every 15 seconds
        - Market closed: refresh every 5 minutes
        """
        status = cls.is_market_open()
        return status.get("is_open", False)
