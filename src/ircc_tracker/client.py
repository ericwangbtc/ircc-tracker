"""Minimal client for the IRCC Application Status Tracker backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import truststore

# Use the operating system trust store. This also handles certificate-chain
# completion on services whose server-provided chain is incomplete.
truststore.inject_into_ssl()

import requests


COGNITO_URL = "https://cognito-idp.ca-central-1.amazonaws.com/"
COGNITO_CLIENT_ID = "3cfutv5ffd1i622g1tn6vton5r"
IRCC_API_URL = "https://api.ircc-tracker-suivi.apps.cic.gc.ca/user"


class IrccError(RuntimeError):
    """Base error for tracker operations."""


class AuthenticationError(IrccError):
    """The supplied tracker credentials were rejected."""


class ApiError(IrccError):
    """The tracker API could not complete a request."""


@dataclass(frozen=True)
class Tokens:
    """Short-lived Cognito tokens held only in process memory."""

    id_token: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class IrccClient:
    """Query one user's tracker account without persisting credentials."""

    def __init__(
        self,
        *,
        timeout: float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.tokens: Optional[Tokens] = None

    def authenticate(self, uci: str, password: str) -> Tokens:
        uci = normalize_uci(uci)
        if not password:
            raise AuthenticationError("Tracker password cannot be empty.")

        response = self._request(
            COGNITO_URL,
            headers={
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": (
                    "AWSCognitoIdentityProviderService.InitiateAuth"
                ),
            },
            json={
                "AuthFlow": "USER_PASSWORD_AUTH",
                "ClientId": COGNITO_CLIENT_ID,
                "AuthParameters": {
                    "USERNAME": uci,
                    "PASSWORD": password,
                },
            },
            operation="authentication",
            authentication_request=True,
        )

        result = response.get("AuthenticationResult")
        if not isinstance(result, dict) or not result.get("IdToken"):
            raise AuthenticationError(
                "IRCC authentication succeeded but returned no ID token."
            )

        self.tokens = Tokens(
            id_token=str(result["IdToken"]),
            access_token=_optional_str(result.get("AccessToken")),
            refresh_token=_optional_str(result.get("RefreshToken")),
            expires_in=_optional_int(result.get("ExpiresIn")),
        )
        return self.tokens

    def get_profile_summary(self, *, limit: int = 50) -> dict[str, Any]:
        return self._api_request(
            {
                "method": "get-profile-summary",
                "startIndex": 0,
                "limit": limit,
                "lob": "",
                "lastActivityDecs": False,
                "searchFilter": "",
                "statusFilter": "",
                "isAgent": False,
            }
        )

    def get_application_details(
        self,
        *,
        application_number: str,
        uci: str,
    ) -> dict[str, Any]:
        application_number = application_number.strip()
        if not application_number:
            raise ValueError("Application number cannot be empty.")

        return self._api_request(
            {
                "method": "get-application-details",
                "applicationNumber": application_number,
                "uci": normalize_uci(uci),
                "isAgent": False,
            }
        )

    def clear_tokens(self) -> None:
        self.tokens = None

    def _api_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.tokens is None:
            raise AuthenticationError("Authenticate before querying IRCC data.")

        return self._request(
            IRCC_API_URL,
            headers={
                "Authorization": f"Bearer {self.tokens.id_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            operation=str(payload.get("method", "API request")),
        )

    def _request(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        operation: str,
        authentication_request: bool = False,
    ) -> dict[str, Any]:
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=json,
                timeout=self.timeout,
            )
        except requests.exceptions.SSLError as exc:
            raise ApiError(
                f"IRCC {operation} TLS certificate verification failed. "
                "Update this application and your operating system certificates."
            ) from exc
        except requests.Timeout as exc:
            raise ApiError(f"IRCC {operation} timed out.") from exc
        except requests.RequestException as exc:
            raise ApiError(f"IRCC {operation} network error: {exc}") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise ApiError(
                f"IRCC {operation} returned non-JSON data (HTTP {response.status_code})."
            ) from exc

        if response.ok:
            if not isinstance(body, dict):
                raise ApiError(f"IRCC {operation} returned an unexpected response.")
            return body

        message = _error_message(body)
        if authentication_request and response.status_code in {400, 401, 403}:
            if "incorrect username or password" in message.lower():
                message = "Incorrect UCI or Tracker password."
            raise AuthenticationError(message)

        if response.status_code == 401:
            raise AuthenticationError(
                "The IRCC session was rejected or has expired. Run the command again."
            )
        if response.status_code == 403:
            raise ApiError(
                "IRCC blocked the request (HTTP 403). Stop and try the official "
                "service later; this tool does not bypass WAF restrictions."
            )

        raise ApiError(
            f"IRCC {operation} failed (HTTP {response.status_code}): {message}"
        )


def normalize_uci(value: str) -> str:
    """Accept formatted UCIs but send Cognito digits only."""

    normalized = value.strip().replace("-", "").replace(" ", "")
    if not normalized.isdigit() or len(normalized) < 8:
        raise ValueError("UCI must contain at least 8 digits.")
    return normalized


def extract_applications(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle profile response shapes observed across tracker versions."""

    for key in ("apps", "applications", "data"):
        value = profile.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    if any(key in profile for key in ("appNum", "appNumber", "applicationNumber")):
        return [profile]
    return []


def application_number(app: dict[str, Any]) -> str:
    for key in ("appNum", "appNumber", "applicationNumber"):
        value = app.get(key)
        if value:
            return str(value)
    return ""


def _error_message(body: Any) -> str:
    if isinstance(body, dict):
        for key in ("message", "error", "error_description", "__type"):
            if body.get(key):
                return str(body[key])
    return "Unknown error"


def _optional_str(value: Any) -> Optional[str]:
    return str(value) if value is not None else None


def _optional_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
