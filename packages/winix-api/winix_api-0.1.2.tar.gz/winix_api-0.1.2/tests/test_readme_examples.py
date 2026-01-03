import os
from pprint import pprint

import pytest
from dotenv import load_dotenv

from winix_api.errors import get_error_message, is_response_error
from winix_api.winix_account import WinixAccount
from winix_api.winix_api import WinixAPI
from winix_api.winix_auth import WinixAuth
from winix_api.winix_types import Airflow,AirQuality, Mode, Plasmawave, Power


@pytest.fixture(scope="module")
def credentials():
    load_dotenv()
    username = os.getenv("WINIX_USERNAME")
    password = os.getenv("WINIX_PASSWORD")
    refresh_token = os.getenv("WINIX_REFRESH_TOKEN")
    user_id = os.getenv("WINIX_USER_ID")
    assert (
        username and password
    ), "Set WINIX_USERNAME and WINIX_PASSWORD in your .env file."
    return username, password, refresh_token, user_id


def test_winix_auth_login(credentials):
    username, password, *_ = credentials
    # Log in with a username and password
    auth = WinixAuth.login(username, password)
    assert hasattr(auth, "access_token")
    pprint(auth)


def test_winix_auth_refresh(credentials):
    _, _, refresh_token, user_id = credentials
    # Refresh an existing session
    if refresh_token and user_id:
        refreshed_auth = WinixAuth.refresh(refresh_token, user_id)
        assert hasattr(refreshed_auth, "access_token")
        pprint(refreshed_auth)
    else:
        pytest.skip("WINIX_REFRESH_TOKEN or WINIX_USER_ID not set")


def test_winix_account_from_credentials(credentials):
    username, password, *_ = credentials
    # Create a WinixAccount from credentials
    account = WinixAccount.from_credentials(username, password)
    assert hasattr(account, "devices")
    pprint(account)


def test_winix_account_from_refresh_token(credentials):
    username, _, refresh_token, user_id = credentials
    # Create a WinixAccount from existing auth credentials
    if refresh_token and user_id:
        account2 = WinixAccount.from_refresh_token(username, refresh_token, user_id)
        assert hasattr(account2, "devices")
        pprint(account2)
    else:
        pytest.skip("WINIX_REFRESH_TOKEN or WINIX_USER_ID not set")


def test_device_listing(credentials):
    username, password, *_ = credentials
    # Get a list of devices associated with the account
    account = WinixAccount.from_credentials(username, password)
    devices = account.devices
    assert isinstance(devices, list)
    for device in devices:
        pprint(device.__dict__)
    if not devices:
        pytest.skip("No devices found.")
    return account, devices


# Fixture to provide a valid account and device_id for device tests
@pytest.fixture(scope="module")
def account_and_device(credentials):
    username, password, *_ = credentials
    account = WinixAccount.from_credentials(username, password)
    devices = account.devices
    if not devices:
        pytest.skip("No devices found.")
    device_id = getattr(devices[0], "deviceId", None) or getattr(
        devices[0], "uuid", None
    )
    assert device_id
    return account, device_id


def test_device_power(account_and_device):
    account, device_id = account_and_device
    # Idempotent set/get for Power
    original = WinixAPI.get_power(account, device_id)
    WinixAPI.set_power(account, device_id, Power.On)
    new_val = WinixAPI.get_power(account, device_id)
    print("power after set:", new_val)
    assert new_val == Power.On
    # Restore
    WinixAPI.set_power(account, device_id, original)


def test_device_mode(account_and_device):
    account, device_id = account_and_device
    # Idempotent set/get for Mode
    original = WinixAPI.get_mode(account, device_id)
    WinixAPI.set_mode(account, device_id, Mode.Auto)
    new_val = WinixAPI.get_mode(account, device_id)
    print("mode after set:", new_val)
    assert new_val == Mode.Auto
    # Restore
    WinixAPI.set_mode(account, device_id, original)


def test_device_airflow(account_and_device):
    account, device_id = account_and_device
    # Idempotent set/get for Airflow
    original = WinixAPI.get_airflow(account, device_id)
    WinixAPI.set_airflow(account, device_id, Airflow.Low)
    new_val = WinixAPI.get_airflow(account, device_id)
    print("airflow after set:", new_val)
    assert new_val == Airflow.Low
    # Restore
    WinixAPI.set_airflow(account, device_id, original)


def test_device_air_quality(account_and_device):
    account, device_id = account_and_device
    # Get the Air Quality
    air_quality = WinixAPI.get_air_quality(account, device_id)
    print("quality:", air_quality)


def test_device_plasmawave(account_and_device):
    account, device_id = account_and_device
    # Idempotent set/get for Plasmawave
    original = WinixAPI.get_plasmawave(account, device_id)
    WinixAPI.set_plasmawave(account, device_id, Plasmawave.Off)
    new_val = WinixAPI.get_plasmawave(account, device_id)
    print("plasmawave after set:", new_val)
    assert new_val == Plasmawave.Off
    # Restore
    WinixAPI.set_plasmawave(account, device_id, original)


def test_device_ambient_light(account_and_device):
    account, device_id = account_and_device
    # Get the Ambient Light
    ambient_light = WinixAPI.get_ambient_light(account, device_id)
    print("ambientLight:", ambient_light)


def test_device_filter_hours(account_and_device):
    account, device_id = account_and_device
    # Get the Filter Hours
    filter_hours = WinixAPI.get_filter_hours(account, device_id)
    print("filterHours:", filter_hours)


def test_error_handling():
    # Error Handling example from README
    assert is_response_error("no data")
    assert get_error_message("no data") == "no data (invalid or unregistered device?)"
