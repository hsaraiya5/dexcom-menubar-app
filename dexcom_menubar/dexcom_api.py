"""Dexcom Share API Client"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class DexcomAPIError(Exception):
    """Base exception for Dexcom API errors"""
    pass


class DexcomAuthenticationError(DexcomAPIError):
    """Authentication failed"""
    pass


class DexcomShareAPI:
    """Client for interacting with Dexcom Share API"""

    # API endpoints
    URLS = {
        'US': 'https://share2.dexcom.com/ShareWebServices/Services',
        'OUS': 'https://shareous1.dexcom.com/ShareWebServices/Services'
    }

    # Trend arrows
    TREND_ARROWS = {
        0: '⚠',   # None
        1: '⬆⬆',  # DoubleUp
        2: '⬆',   # SingleUp
        3: '↗',   # FortyFiveUp
        4: '→',   # Flat
        5: '↘',   # FortyFiveDown
        6: '⬇',   # SingleDown
        7: '⬇⬇',  # DoubleDown
        8: '⚠',   # NotComputable
        9: '⚠'    # RateOutOfRange
    }

    TREND_NAMES = {
        0: 'None',
        1: 'DoubleUp',
        2: 'SingleUp',
        3: 'FortyFiveUp',
        4: 'Flat',
        5: 'FortyFiveDown',
        6: 'SingleDown',
        7: 'DoubleDown',
        8: 'NotComputable',
        9: 'RateOutOfRange'
    }

    def __init__(self, username: str, password: str, region: str = 'US'):
        """
        Initialize Dexcom Share API client

        Args:
            username: Dexcom Share username
            password: Dexcom Share password
            region: Region ('US' or 'OUS' for Outside US)
        """
        self.username = username
        self.password = password
        self.region = region.upper()

        if self.region not in self.URLS:
            raise ValueError(f"Invalid region: {region}. Must be 'US' or 'OUS'")

        self.base_url = self.URLS[self.region]
        self.session_id: Optional[str] = None
        self.account_id: Optional[str] = None

        # Application ID - this is the official Dexcom Share app ID
        self.application_id = "d89443d2-327c-4a6f-89e5-496bbb0317db"

    def authenticate(self) -> bool:
        """
        Authenticate with Dexcom Share API

        Returns:
            True if authentication successful

        Raises:
            DexcomAuthenticationError: If authentication fails
        """
        try:
            # First, get account ID
            auth_url = f"{self.base_url}/General/AuthenticatePublisherAccount"

            payload = {
                "accountName": self.username,
                "password": self.password,
                "applicationId": self.application_id
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Dexcom Share/3.0.2.11 CFNetwork/711.2.23 Darwin/14.0.0"
            }

            logger.info("Authenticating with Dexcom Share API...")
            response = requests.post(auth_url, json=payload, headers=headers)

            if response.status_code != 200:
                raise DexcomAuthenticationError(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )

            self.account_id = response.json()

            if not self.account_id or self.account_id == "00000000-0000-0000-0000-000000000000":
                raise DexcomAuthenticationError("Invalid credentials")

            # Now login to get session ID
            login_url = f"{self.base_url}/General/LoginPublisherAccountById"

            payload = {
                "accountId": self.account_id,
                "password": self.password,
                "applicationId": self.application_id
            }

            response = requests.post(login_url, json=payload, headers=headers)

            if response.status_code != 200:
                raise DexcomAuthenticationError(
                    f"Login failed: {response.status_code} - {response.text}"
                )

            self.session_id = response.json()

            if not self.session_id:
                raise DexcomAuthenticationError("Failed to obtain session ID")

            logger.info("Successfully authenticated with Dexcom Share API")
            return True

        except requests.exceptions.RequestException as e:
            raise DexcomAPIError(f"Network error during authentication: {str(e)}")

    def get_current_glucose(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent glucose reading

        Returns:
            Dictionary with glucose reading data or None if no data available
        """
        readings = self.get_glucose_readings(max_count=1)
        return readings[0] if readings else None

    def get_glucose_readings(self, max_count: int = 12, minutes: int = 1440) -> List[Dict[str, Any]]:
        """
        Get glucose readings from Dexcom Share

        Args:
            max_count: Maximum number of readings to retrieve (default 12)
            minutes: Number of minutes to look back (default 1440 = 24 hours)

        Returns:
            List of glucose reading dictionaries

        Raises:
            DexcomAPIError: If API request fails
        """
        if not self.session_id:
            logger.info("No session ID, authenticating...")
            self.authenticate()

        try:
            url = f"{self.base_url}/Publisher/ReadPublisherLatestGlucoseValues"

            params = {
                "sessionId": self.session_id,
                "minutes": minutes,
                "maxCount": max_count
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Dexcom Share/3.0.2.11 CFNetwork/711.2.23 Darwin/14.0.0"
            }

            response = requests.post(url, params=params, headers=headers)

            if response.status_code == 500:
                # Session expired, re-authenticate
                logger.info("Session expired, re-authenticating...")
                self.authenticate()
                return self.get_glucose_readings(max_count, minutes)

            if response.status_code != 200:
                raise DexcomAPIError(
                    f"Failed to get glucose readings: {response.status_code} - {response.text}"
                )

            raw_readings = response.json()

            # Parse and format readings
            readings = []
            for reading in raw_readings:
                readings.append(self._parse_reading(reading))

            return readings

        except requests.exceptions.RequestException as e:
            raise DexcomAPIError(f"Network error: {str(e)}")

    def _parse_reading(self, raw_reading: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw API reading into formatted dictionary"""
        # Convert Dexcom timestamp (milliseconds since epoch)
        # Handle both /Date(...)/ and Date(...) formats
        timestamp_str = raw_reading['WT']
        timestamp_str = timestamp_str.replace('/Date(', '').replace(')/', '')
        timestamp_str = timestamp_str.replace('Date(', '').replace(')', '')
        timestamp_ms = int(timestamp_str)
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

        # Get trend value - handle both string and integer formats
        trend = raw_reading.get('Trend', 0)

        # If trend is a string name, convert it to the integer value
        if isinstance(trend, str):
            # Map string names to integer values
            trend_map = {
                'None': 0,
                'DoubleUp': 1,
                'SingleUp': 2,
                'FortyFiveUp': 3,
                'Flat': 4,
                'FortyFiveDown': 5,
                'SingleDown': 6,
                'DoubleDown': 7,
                'NotComputable': 8,
                'RateOutOfRange': 9
            }
            trend = trend_map.get(trend, 0)

        logger.debug(f"Raw reading: {raw_reading}")
        logger.debug(f"Parsed trend: {trend} -> {self.TREND_ARROWS.get(trend, '?')}")

        return {
            'value': raw_reading['Value'],
            'trend': trend,
            'trend_arrow': self.TREND_ARROWS.get(trend, '?'),
            'trend_name': self.TREND_NAMES.get(trend, 'Unknown'),
            'timestamp': timestamp,
            'timestamp_str': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_trend_arrow(self, trend: int) -> str:
        """Get trend arrow symbol for a trend value"""
        return self.TREND_ARROWS.get(trend, '?')
