#!/usr/bin/env python3
"""Add account to Twscrape pool using cookies."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from twscrape import API
from src.auth.account_manager import AccountManager


async def add_account_from_cookies():
    """Add BigSky_7 account to Twscrape using cookies."""
    print("Twscrape Account Pool Setup")
    print("=" * 60)

    # Initialize API
    api = API()

    # Load cookies
    am = AccountManager("config/cookies.json")
    cookies = am.load_cookies()
    auth_token = am.get_auth_token()

    print(f"\n✓ Loaded cookies for @BigSky_7")
    print(f"  Auth token: {auth_token[:20]}...")
    print(f"  Total cookies: {len(cookies)}")

    # Check current accounts
    try:
        accounts = await api.pool.accounts_info()
        print(f"\n✓ Current accounts in pool: {len(accounts)}")

        if len(accounts) > 0:
            print("\nExisting accounts:")
            for acc in accounts:
                print(f"  - {acc.username} (active: {acc.active})")
            return api
    except Exception as e:
        print(f"\nℹ️  No accounts in pool yet")

    # Convert cookies to Twscrape format (JSON string)
    cookies_str = json.dumps(cookies)

    print("\n✓ Adding account with cookies...")
    try:
        # Add account using cookies (password/email can be dummy values when using cookies)
        await api.pool.add_account(
            username="BigSky_7",
            password="",           # Not needed with cookies
            email="",              # Not needed with cookies
            email_password="",     # Not needed with cookies
            cookies=cookies_str
        )
        print("✓ Account added to pool!")

        # Login using the cookies
        print("\n✓ Logging in with cookies...")
        await api.pool.login_all()
        print("✓ Login successful!")

        # Verify
        accounts = await api.pool.accounts_info()
        print(f"\n✓ Account pool ready!")
        print(f"  Total accounts: {len(accounts)}")
        for acc in accounts:
            # Handle both dict and object types
            if isinstance(acc, dict):
                print(f"  - {acc.get('username', 'BigSky_7')}: active={acc.get('active', True)}")
            else:
                print(f"  - {acc.username}: active={acc.active}")

    except Exception as e:
        print(f"\n✗ Error adding account: {e}")
        print(f"\nDetails: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    return api


if __name__ == "__main__":
    asyncio.run(add_account_from_cookies())
