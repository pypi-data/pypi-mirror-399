import requests

from winix_api.errors import get_error_message, is_response_error
from winix_api.winix_account import WinixAccount
from winix_api.winix_types import (
    Airflow,
    AirQuality,
    Attribute,
    DeviceStatus,
    Mode,
    Plasmawave,
    Power,
)

URL_DEVICE_STATUS = (
    "https://us.api.winix-iot.com/common/event/sttus/devices/{device_id}"
)
URL_SET_ATTRIBUTE = "https://us.api.winix-iot.com/common/control/devices/{device_id}/A211/{attribute}:{value}"


class WinixAPI:
    """
    API for interacting with Winix devices: status, attributes, and control.
    """

    @staticmethod
    def get_device_status(account: WinixAccount, device_id: str) -> DeviceStatus:
        url = URL_DEVICE_STATUS.format(device_id=device_id)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        headers = data.get("headers", {})
        result_message = headers.get("resultMessage", "")
        body = data.get("body", {})
        if is_response_error(result_message) or not body or not body.get("data"):
            raise Exception(get_error_message(result_message))
        attributes = body["data"][0]["attributes"]
        return DeviceStatus(
            power=Power(attributes.get(Attribute.Power)),
            mode=Mode(attributes.get(Attribute.Mode)),
            airflow=Airflow(attributes.get(Attribute.Airflow)),
            air_quality=AirQuality(attributes.get(Attribute.AirQuality)),
            plasmawave=Plasmawave(attributes.get(Attribute.Plasmawave)),
            ambient_light=int(attributes.get(Attribute.AmbientLight, -1)),
            filter_hours=int(attributes.get(Attribute.FilterHours, -1)),
        )

    @staticmethod
    def get_device_attribute(
        account: WinixAccount, device_id: str, attribute: Attribute
    ) -> object:
        status = WinixAPI.get_device_status(account, device_id)
        return getattr(status, attribute.name.lower(), None)

    @staticmethod
    def set_device_attribute(
        account: WinixAccount, device_id: str, attribute: Attribute, value: str
    ) -> str:
        url = URL_SET_ATTRIBUTE.format(
            device_id=device_id, attribute=attribute.value, value=value
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        headers = data.get("headers", {})
        result_message = headers.get("resultMessage", "")
        if is_response_error(result_message):
            raise Exception(get_error_message(result_message))
        return value

    @staticmethod
    def get_power(account: WinixAccount, device_id: str) -> Power:
        return WinixAPI.get_device_attribute(account, device_id, Attribute.Power)

    @staticmethod
    def set_power(account: WinixAccount, device_id: str, value: Power) -> str:
        return WinixAPI.set_device_attribute(
            account, device_id, Attribute.Power, value.value
        )

    @staticmethod
    def get_mode(account: WinixAccount, device_id: str) -> Mode:
        return WinixAPI.get_device_attribute(account, device_id, Attribute.Mode)

    @staticmethod
    def set_mode(account: WinixAccount, device_id: str, value: Mode) -> str:
        return WinixAPI.set_device_attribute(
            account, device_id, Attribute.Mode, value.value
        )

    @staticmethod
    def get_airflow(account: WinixAccount, device_id: str) -> Airflow:
        return WinixAPI.get_device_attribute(account, device_id, Attribute.Airflow)

    @staticmethod
    def set_airflow(account: WinixAccount, device_id: str, value: Airflow) -> str:
        return WinixAPI.set_device_attribute(
            account, device_id, Attribute.Airflow, value.value
        )

    @staticmethod
    def get_air_quality(account: WinixAccount, device_id: str) -> AirQuality:
        return WinixAPI.get_device_attribute(account, device_id, Attribute.AirQuality)

    @staticmethod
    def get_plasmawave(account: WinixAccount, device_id: str) -> Plasmawave:
        return WinixAPI.get_device_attribute(account, device_id, Attribute.Plasmawave)

    @staticmethod
    def set_plasmawave(account: WinixAccount, device_id: str, value: Plasmawave) -> str:
        return WinixAPI.set_device_attribute(
            account, device_id, Attribute.Plasmawave, value.value
        )

    @staticmethod
    def get_ambient_light(account: WinixAccount, device_id: str) -> int:
        value = WinixAPI.get_device_attribute(
            account, device_id, Attribute.AmbientLight
        )
        try:
            return int(value)
        except (TypeError, ValueError):
            return -1

    @staticmethod
    def get_filter_hours(account: WinixAccount, device_id: str) -> int:
        value = WinixAPI.get_device_attribute(account, device_id, Attribute.FilterHours)
        try:
            return int(value)
        except (TypeError, ValueError):
            return -1
