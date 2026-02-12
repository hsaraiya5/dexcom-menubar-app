"""Interactive setup script for Dexcom Menubar credentials"""

import sys
import getpass
from dexcom_menubar.credentials import CredentialManager
from dexcom_menubar.dexcom_api import DexcomShareAPI, DexcomAuthenticationError, DexcomAPIError


def main():
    """Interactive credential setup"""
    print("\n" + "=" * 60)
    print("Dexcom Menubar - Credential Setup")
    print("=" * 60 + "\n")

    print("This will securely store your Dexcom Share credentials")
    print("in the macOS Keychain.\n")

    # Check if credentials already exist
    if CredentialManager.has_credentials():
        response = input("Credentials already exist. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled.")
            sys.exit(0)
        print()

    # Get username
    username = input("Dexcom Share Username: ").strip()
    if not username:
        print("\nError: Username cannot be empty.")
        sys.exit(1)

    # Get password (hidden input)
    password = getpass.getpass("Dexcom Share Password: ")
    if not password:
        print("\nError: Password cannot be empty.")
        sys.exit(1)

    # Get region
    print("\nSelect your region:")
    print("  1) US (United States)")
    print("  2) OUS (Outside US)")
    region_choice = input("Enter choice (1 or 2) [1]: ").strip() or "1"

    if region_choice == "1":
        region = "US"
    elif region_choice == "2":
        region = "OUS"
    else:
        print("\nError: Invalid choice. Using US.")
        region = "US"

    print(f"\nRegion selected: {region}")

    # Test credentials
    print("\nTesting credentials...")
    try:
        api = DexcomShareAPI(username, password, region)
        api.authenticate()
        print("✓ Authentication successful!")

        # Try to get a reading
        reading = api.get_current_glucose()
        if reading:
            print(f"✓ Current glucose: {reading['value']} mg/dL {reading['trend_arrow']}")
        else:
            print("⚠ Authentication worked but no glucose data available.")

    except DexcomAuthenticationError as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nPlease verify:")
        print("  - Your username and password are correct")
        print("  - Share is enabled in the Dexcom app")
        print("  - You selected the correct region")
        response = input("\nSave credentials anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled.")
            sys.exit(1)
    except DexcomAPIError as e:
        print(f"\n⚠ API Error: {e}")
        print("Credentials may be correct but there was a network issue.")
        response = input("\nSave credentials anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        response = input("\nSave credentials anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled.")
            sys.exit(1)

    # Save credentials
    print("\nSaving credentials to macOS Keychain...")
    if CredentialManager.save_credentials(username, password, region):
        print("✓ Credentials saved successfully!\n")
        print("You can now run the menubar app:")
        print("  ./run.sh")
        print("  or")
        print("  python -m dexcom_menubar.app\n")
        sys.exit(0)
    else:
        print("✗ Failed to save credentials.")
        print("Check that you have permission to access the Keychain.\n")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
