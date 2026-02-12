"""Credential management for Dexcom Share"""

import keyring
import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

SERVICE_NAME = "DexcomMenubar"


class CredentialManager:
    """Manage Dexcom Share credentials securely"""

    @staticmethod
    def get_credentials() -> Tuple[Optional[str], Optional[str], str]:
        """
        Get Dexcom Share credentials

        Priority:
        1. Environment variables
        2. macOS Keychain

        Returns:
            Tuple of (username, password, region)
        """
        # Try environment variables first
        username = os.environ.get('DEXCOM_USERNAME')
        password = os.environ.get('DEXCOM_PASSWORD')
        region = os.environ.get('DEXCOM_REGION', 'US')

        if username and password:
            logger.info("Using credentials from environment variables")
            return username, password, region

        # Try keychain
        try:
            username = keyring.get_password(SERVICE_NAME, "username")
            password = keyring.get_password(SERVICE_NAME, "password")
            region = keyring.get_password(SERVICE_NAME, "region") or 'US'

            if username and password:
                logger.info("Using credentials from keychain")
                return username, password, region
        except Exception as e:
            logger.warning(f"Failed to retrieve credentials from keychain: {e}")

        return None, None, region

    @staticmethod
    def save_credentials(username: str, password: str, region: str = 'US') -> bool:
        """
        Save credentials to macOS Keychain

        Args:
            username: Dexcom Share username
            password: Dexcom Share password
            region: Region ('US' or 'OUS')

        Returns:
            True if successful
        """
        try:
            keyring.set_password(SERVICE_NAME, "username", username)
            keyring.set_password(SERVICE_NAME, "password", password)
            keyring.set_password(SERVICE_NAME, "region", region)
            logger.info("Credentials saved to keychain")
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials to keychain: {e}")
            return False

    @staticmethod
    def delete_credentials() -> bool:
        """
        Delete credentials from keychain

        Returns:
            True if successful
        """
        try:
            keyring.delete_password(SERVICE_NAME, "username")
            keyring.delete_password(SERVICE_NAME, "password")
            keyring.delete_password(SERVICE_NAME, "region")
            logger.info("Credentials deleted from keychain")
            return True
        except Exception as e:
            logger.error(f"Failed to delete credentials from keychain: {e}")
            return False

    @staticmethod
    def has_credentials() -> bool:
        """Check if credentials are available"""
        username, password, _ = CredentialManager.get_credentials()
        return username is not None and password is not None
