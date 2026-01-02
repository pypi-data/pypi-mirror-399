import base64
import contextlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Iterator, TypedDict

import filelock
import requests

EXPIRY_LEEWAY_SECOND = 300


class DeviceCodeFlow(TypedDict):
    verification_uri_complete: str
    interval: int
    device_code: str


class CLIAuthTokens(TypedDict):
    access_token: str
    id_token: str
    refresh_token: str
    expires_at: int


class IDTokenClaims(TypedDict):
    name: str
    email: str


def tokens_json_path() -> Path:
    vitalx_dir = Path.home() / ".vitalx"
    vitalx_dir.mkdir(mode=770, parents=True, exist_ok=True)
    return vitalx_dir / "tokens.json"


@contextlib.contextmanager
def readwrite_tokens_json() -> Iterator[Path]:
    path = tokens_json_path()
    with filelock.FileLock(path.with_suffix(".lock")):
        yield path


def current_tokens(refresh_if_needed: bool = False) -> CLIAuthTokens | None:
    try:
        with open(tokens_json_path(), "rt") as f:
            tokens: CLIAuthTokens = json.loads(f.read())

        if refresh_if_needed:
            tokens = _check_and_refresh(tokens)

        return tokens

    except OSError:
        return None


def initiate_device_code_flow() -> DeviceCodeFlow:
    resp = requests.post(
        "https://auth.tryvital.io/oauth/device/code",
        data={
            "client_id": "2Ftm264vkCOvXaLX0NZi3Yp8nyDrYGgv",
            "audience": "https://api.tryvital.io",
            "scope": "openid email profile offline_access",
        },
    )
    resp.raise_for_status()

    return resp.json()


def get_userinfo(id_token: str) -> IDTokenClaims:
    components = id_token.split(".")

    if len(components) != 3:
        raise ValueError("Invalid ID Token")

    claims = json.loads(base64.b64decode(components[1] + "==").decode())
    return claims


def poll_for_device_code_flow_completion(flow: DeviceCodeFlow) -> None:
    with readwrite_tokens_json() as tokens_json_path:
        start_dt = datetime.now()

        while True:
            now_dt = datetime.now()

            if (now_dt - start_dt).total_seconds() >= 180:
                raise RuntimeError(
                    "More than 180 seconds have elapsed since the login flow was started. "
                    "Please restart the login flow."
                )

            form_data = {
                "client_id": "2Ftm264vkCOvXaLX0NZi3Yp8nyDrYGgv",
                "device_code": flow["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }

            resp = requests.post("https://auth.tryvital.io/oauth/token", data=form_data)

            if resp.status_code == 200:
                auth0_response = resp.json()
                new_tokens: CLIAuthTokens = {
                    "access_token": auth0_response["access_token"],
                    "id_token": auth0_response["id_token"],
                    "refresh_token": auth0_response["refresh_token"],
                    "expires_at": int(_now() + auth0_response["expires_in"]),
                }

                with open(tokens_json_path, "w") as f:
                    f.write(json.dumps(new_tokens, indent=2))
                    f.flush()
                    os.fsync(f.fileno())

                return

            if resp.status_code in (403, 429):
                match resp.json()["error"]:
                    case "slow_down" | "authorization_pending":
                        sleep(float(flow["interval"]))
                        continue

                    case "expired_token":
                        raise RuntimeError(
                            "The authentication session has expired. Please restart the command."
                        )

                    case "access_denied":
                        raise RuntimeError(
                            "You denied access during the authentication flow."
                        )

            raise RuntimeError("Unknown error: ", resp.status_code, resp.text)


def _check_and_refresh(tokens: CLIAuthTokens) -> CLIAuthTokens:
    with readwrite_tokens_json() as tokens_json_path:
        # Re-read again in case the previous lock holder has updated the tokens.
        latest_tokens = current_tokens() or tokens

        if _now() <= (tokens["expires_at"] - EXPIRY_LEEWAY_SECOND):
            return latest_tokens

        form_data = {
            "client_id": "2Ftm264vkCOvXaLX0NZi3Yp8nyDrYGgv",
            "refresh_token": latest_tokens["refresh_token"],
            "grant_type": "refresh_token",
        }

        resp = requests.post("https://auth.tryvital.io/oauth/token", data=form_data)
        resp.raise_for_status()

        auth0_response = resp.json()

        new_tokens: CLIAuthTokens = {
            "access_token": auth0_response["access_token"],
            "id_token": auth0_response["id_token"],
            "refresh_token": auth0_response.get("refresh_token")
            or latest_tokens["refresh_token"],
            "expires_at": int(_now() + auth0_response["expires_in"]),
        }

        with open(tokens_json_path, "w") as f:
            f.write(json.dumps(new_tokens, indent=2))
            f.flush()
            os.fsync(f.fileno())

        return new_tokens


def _now() -> int:
    return int(datetime.now(timezone.utc).timestamp())
