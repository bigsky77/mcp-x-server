"""Account and authentication management."""

import json
from pathlib import Path
from typing import Dict, List, Optional


class AuthError(Exception):
    """Raised when authentication fails."""

    pass


class AccountManager:
    """Manages authentication for TwiKit and Twscrape."""

    def __init__(self, cookies_file: str, accounts_file: Optional[str] = None):
        self.cookies_file = Path(cookies_file)
        self.accounts_file = Path(accounts_file) if accounts_file else None
        self._cookies: Optional[Dict] = None

    def load_cookies(self) -> Dict:
        """Load cookies from file for TwiKit authentication."""
        if self._cookies is not None:
            return self._cookies

        if not self.cookies_file.exists():
            raise AuthError(f"Cookies file not found: {self.cookies_file}")

        try:
            with open(self.cookies_file) as f:
                self._cookies = json.load(f)
            return self._cookies
        except json.JSONDecodeError as e:
            raise AuthError(f"Invalid cookies file: {e}")

    def get_auth_token(self) -> Optional[str]:
        """Extract auth_token from cookies."""
        cookies = self.load_cookies()
        for cookie in cookies:
            if cookie.get("name") == "auth_token":
                return cookie.get("value")
        return None

    def get_ct0_token(self) -> Optional[str]:
        """Extract ct0 (csrf token) from cookies."""
        cookies = self.load_cookies()
        for cookie in cookies:
            if cookie.get("name") == "ct0":
                return cookie.get("value")
        return None

    def save_cookies(self, cookies: List[Dict]):
        """Save updated cookies back to file."""
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        self._cookies = cookies

    def get_twscrape_accounts(self) -> List[str]:
        """
        Get list of accounts for Twscrape.

        For Phase 1, returns empty list (no account pool yet).
        """
        if not self.accounts_file or not self.accounts_file.exists():
            return []

        with open(self.accounts_file) as f:
            accounts = json.load(f)
        return accounts
