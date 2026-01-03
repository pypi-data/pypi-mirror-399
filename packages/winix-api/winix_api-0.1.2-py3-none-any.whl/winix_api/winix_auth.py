import logging
import time

from warrant_lite import WarrantLite

from winix_api.winix_auth_response import WinixAuthResponse

USER_POOL_ID = "us-east-1_Ofd50EosD"
CLIENT_ID = "14og512b9u20b8vrdm55d8empi"
CLIENT_SECRET = "k554d4pvgf2n0chbhgtmbe4q0ul4a9flp3pcl6a47ch6rripvvr"
REGION = "us-east-1"


class RefreshTokenExpiredError(Exception):
    """Raised when the refresh token is expired or invalid."""

    pass


class WinixAuth:
    @staticmethod
    def login(username: str, password: str, max_attempts: int = 5) -> WinixAuthResponse:
        wl = WarrantLite(
            username=username,
            password=password,
            pool_id=USER_POOL_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            pool_region=REGION,
        )
        for attempt in range(max_attempts):
            try:
                tokens = wl.authenticate_user()
                logging.debug(f"tokens returned from WarrantLite: {tokens}")
                sub = None
                if (
                    "id_token" in tokens
                    and isinstance(tokens["id_token"], dict)
                    and "sub" in tokens["id_token"]
                ):
                    sub = tokens["id_token"]["sub"]
                elif (
                    "AuthenticationResult" in tokens
                    and "IdToken" in tokens["AuthenticationResult"]
                ):
                    import jwt

                    decoded = jwt.decode(
                        tokens["AuthenticationResult"]["IdToken"],
                        options={"verify_signature": False},
                    )
                    sub = decoded.get("sub")
                elif (
                    "AuthenticationResult" in tokens
                    and "AccessToken" in tokens["AuthenticationResult"]
                ):
                    import jwt

                    decoded = jwt.decode(
                        tokens["AuthenticationResult"]["AccessToken"],
                        options={"verify_signature": False},
                    )
                    sub = decoded.get("sub")
                if not sub:
                    logging.error("Could not extract 'sub' (user_id) from tokens.")
                    continue
                return WinixAuthResponse(
                    user_id=sub,
                    access_token=tokens["AuthenticationResult"]["AccessToken"],
                    expires_at=WinixAuth.to_expires_at(
                        tokens["AuthenticationResult"]["ExpiresIn"]
                    ),
                    refresh_token=tokens["AuthenticationResult"]["RefreshToken"],
                )
            except Exception as e:
                logging.warning(
                    f"Exception during authentication attempt {attempt+1}: {e}"
                )
                time.sleep(3)
        raise Exception("Failed to authenticate after max attempts")

    @staticmethod
    def refresh(refresh_token: str, user_id: str) -> WinixAuthResponse:
        wl = WarrantLite(
            username=user_id,
            password=None,
            pool_id=USER_POOL_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            pool_region=REGION,
        )
        try:
            tokens = wl.refresh_tokens(refresh_token)
            return WinixAuthResponse(
                user_id=user_id,
                access_token=tokens["AuthenticationResult"]["AccessToken"],
                expires_at=WinixAuth.to_expires_at(
                    tokens["AuthenticationResult"]["ExpiresIn"]
                ),
                refresh_token=refresh_token,
            )
        except Exception as e:
            raise RefreshTokenExpiredError(f"Refresh token expired or invalid: {e}")

    @staticmethod
    def to_expires_at(expires_in: int) -> int:
        return int(time.time() * 1000) + int(expires_in) * 1000
