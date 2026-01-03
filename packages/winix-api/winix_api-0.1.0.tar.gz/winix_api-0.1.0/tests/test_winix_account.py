import os
from pprint import pprint

from dotenv import load_dotenv

from winix_api.winix_account import WinixAccount


def test_winix_device_listing():
    """
    End-to-end test for Winix device listing.
    Loads credentials, authenticates, fetches devices, and asserts results.
    """
    load_dotenv()
    username = os.getenv("WINIX_USERNAME")
    password = os.getenv("WINIX_PASSWORD")
    assert username, "WINIX_USERNAME not set"
    assert password, "WINIX_PASSWORD not set"

    account = WinixAccount.from_credentials(username, password)
    devices = account.devices
    assert isinstance(devices, list), "Devices should be a list"
    print(f"Found {len(devices)} devices:")
    for device in devices:
        pprint(device.__dict__)
    if devices:
        assert hasattr(devices[0], "uuid") or hasattr(devices[0], "deviceId"), "Device missing expected attributes"
