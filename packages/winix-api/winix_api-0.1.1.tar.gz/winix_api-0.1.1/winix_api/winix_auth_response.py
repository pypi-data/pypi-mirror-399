from dataclasses import dataclass


@dataclass
class WinixAuthResponse:
    user_id: str
    access_token: str
    expires_at: int
    refresh_token: str
