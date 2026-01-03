import time
import zlib

import requests

from winix_api.errors import get_error_message, is_response_error
from winix_api.winix_auth import WinixAuth, WinixAuthResponse

TOKEN_EXPIRY_BUFFER = 10 * 60 * 1000
URL_GET_DEVICES = "https://us.mobile.winix-iot.com/getDeviceInfoList"
URL_REGISTER_USER = "https://us.mobile.winix-iot.com/registerUser"
URL_CHECK_ACCESS_TOKEN = "https://us.mobile.winix-iot.com/checkAccessToken"
COGNITO_CLIENT_SECRET_KEY = "k554d4pvgf2n0chbhgtmbe4q0ul4a9flp3pcl6a47ch6rripvvr"


class WinixDevice:
    """Represents a Winix device."""

    def __init__(self, device_info):
        self.__dict__.update(device_info)


class WinixAccount:
    """
    Represents a Winix user account, providing device listing and token management.
    """

    def __init__(self, username: str, auth: WinixAuthResponse):
        self.username = username
        self.auth = auth
        self.uuid = self._generate_uuid(auth.access_token)
        self._devices = None
        self._register_user()
        self._check_access_token()

    @classmethod
    def from_credentials(cls, username: str, password: str):
        auth = WinixAuth.login(username, password)
        return cls(username, auth)

    @classmethod
    def from_refresh_token(cls, username: str, refresh_token: str, user_id: str):
        auth = WinixAuth.refresh(refresh_token, user_id)
        return cls(username, auth)

    @property
    def devices(self):
        if self._devices is None:
            self._devices = self._fetch_devices()
        return self._devices

    def _fetch_devices(self):
        self._refresh_if_expired()
        response = requests.post(
            URL_GET_DEVICES,
            json={
                "accessToken": self.auth.access_token,
                "uuid": self.uuid,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [WinixDevice(d) for d in data.get("deviceInfoList", [])]

    def _refresh_if_expired(self):
        if self._is_expired():
            self.auth = WinixAuth.refresh(self.auth.refresh_token, self.auth.user_id)
            self.uuid = self._generate_uuid(self.auth.access_token)
            self._register_user()
            self._check_access_token()
            self._devices = None

    def _is_expired(self):
        return (
            not self.auth.access_token
            or self.auth.expires_at <= int(time.time() * 1000) - TOKEN_EXPIRY_BUFFER
        )

    def _register_user(self):
        payload = {
            "cognitoClientSecretKey": COGNITO_CLIENT_SECRET_KEY,
            "accessToken": self.auth.access_token,
            "uuid": self.uuid,
            "email": self.username,
            "osType": "android",
            "osVersion": "29",
            "mobileLang": "en",
        }
        response = requests.post(URL_REGISTER_USER, json=payload)
        response.raise_for_status()

    def _check_access_token(self):
        payload = {
            "cognitoClientSecretKey": COGNITO_CLIENT_SECRET_KEY,
            "accessToken": self.auth.access_token,
            "uuid": self.uuid,
            "osVersion": "29",
            "mobileLang": "en",
        }
        response = requests.post(URL_CHECK_ACCESS_TOKEN, json=payload)
        response.raise_for_status()

    @staticmethod
    def _generate_uuid(access_token):
        import jwt

        decoded = jwt.decode(access_token, options={"verify_signature": False})
        sub = decoded["sub"]
        userid_b = sub.encode()
        p1 = format(zlib.crc32(b"github.com/regaw-leinad/winix-api" + userid_b), "x")
        p2 = format(zlib.crc32(b"HGF" + userid_b), "x")
        return f"{p1}{p2}"
