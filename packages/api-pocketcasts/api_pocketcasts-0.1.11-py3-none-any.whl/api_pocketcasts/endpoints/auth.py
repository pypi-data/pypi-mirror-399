# Authentication endpoints and helpers for Pocket Casts API.
# Stateless, in-memory only. No credentials or tokens are ever persisted to disk.

import httpx
from api_pocketcasts.models import (
    User,
    SubscriptionStatus,
    SubscriptionTier,
    SubscriptionFeatures,
    SubscriptionWeb,
)
from api_pocketcasts.exceptions import (
    PocketCastsAuthError,
    PocketCastsTokenExpiredError,
)


def login_pocket_casts(email: str, password: str) -> User:
    """
    Log in to Pocket Casts and return a User object.
    Args:
        email (str): User's email address.
        password (str): User's password.
    Returns:
        User: The authenticated user object with tokens and metadata.
    Raises:
        PocketCastsAuthError: If authentication fails or an error occurs
            (e.g., invalid credentials, network error).
    """
    url = "https://api.pocketcasts.com/user/login_pocket_casts"
    try:
        response = httpx.post(
            url,
            json={"email": email, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return User(
            email=data["email"],
            uuid=data["uuid"],
            is_new=data.get("isNew", False),
            access_token=data["accessToken"],
            token_type=data["tokenType"],
            expires_in=data["expiresIn"],
            refresh_token=data["refreshToken"],
        )
    except httpx.HTTPStatusError as e:
        error_id = ""
        error_text = ""
        error_details = {}
        if hasattr(e.response, "json"):
            try:
                error_data = e.response.json()
                error_id = error_data.get("errorMessageId", "").lower()
                error_text = (
                    e.response.text if hasattr(e.response, "text") else str(error_data)
                )
                error_details = error_data
            except Exception:
                error_text = (
                    e.response.text if hasattr(e.response, "text") else str(e.response)
                )
                error_details = {"raw_response": error_text}
        if "token" in error_id or "auth" in error_id:
            raise PocketCastsTokenExpiredError(
                message="Token error during login.",
                details={
                    "error_id": error_id,
                    "error_text": error_text,
                    **error_details,
                },
            )
        raise PocketCastsAuthError(
            message="Login failed.",
            details={
                "error_id": error_id,
                "error_text": error_text,
                **error_details,
            },
        )
    except Exception as e:
        raise PocketCastsAuthError(
            message="Unexpected error during login.", details={"exception": str(e)}
        )


def clear_credentials():
    """
    Clear credentials from memory (no-op for stateless client).
    Placeholder for future in-memory cleanup if needed.
    """
    pass


def refresh_token(refresh_token: str) -> User:
    """
    Refresh the Pocket Casts access token using the /user/token endpoint.
    Args:
        refresh_token (str): The refresh token string.
    Returns:
        User: The refreshed user object with new tokens and metadata.
    Raises:
        PocketCastsAuthError: If the refresh fails (e.g., invalid/expired token, network error).
    """
    url = "https://api.pocketcasts.com/user/token"
    try:
        response = httpx.post(
            url,
            json={"grantType": "refresh_token", "refreshToken": refresh_token},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return User(
            email=data["email"],
            uuid=data["uuid"],
            is_new=data.get("isNew", False),
            access_token=data["accessToken"],
            token_type=data["tokenType"],
            expires_in=data["expiresIn"],
            refresh_token=data["refreshToken"],
        )
    except httpx.HTTPStatusError as e:
        error_id = ""
        error_text = ""
        error_details = {}
        if hasattr(e.response, "json"):
            try:
                error_data = e.response.json()
                error_id = error_data.get("error") or error_data.get("error_id") or ""
                error_id = (
                    error_id.lower() if isinstance(error_id, str) else str(error_id)
                )
                error_text = (
                    error_data.get("error_description")
                    or error_data.get("error_text")
                    or e.response.text
                )
                error_details = error_data
            except Exception:
                error_text = (
                    e.response.text if hasattr(e.response, "text") else str(e.response)
                )
                error_details = {"raw_response": error_text}
        if error_id == "invalid_grant":
            raise PocketCastsTokenExpiredError(
                message="Token refresh error.",
                details={
                    "error": error_id,
                    "error_description": error_text,
                    **error_details,
                },
            )
        raise PocketCastsAuthError(
            message="Token refresh failed.",
            details={
                "error": error_id,
                "error_description": error_text,
                **error_details,
            },
        )
    except Exception as e:
        raise PocketCastsAuthError(
            message="Unexpected error during token refresh.",
            details={"exception": str(e)},
        )


def get_subscription_status(token: str) -> SubscriptionStatus:
    """
    Fetch the user's subscription status from the /subscription/status endpoint.
    Args:
        token (str): Bearer access token.
    Returns:
        SubscriptionStatus: The user's subscription status and tier info.
    Raises:
        PocketCastsAuthError: If the request fails or the token is invalid/expired.
    """
    url = "https://api.pocketcasts.com/subscription/status"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Map API fields to model fields (convert camelCase to snake_case)
        features = data.get("features", {})
        web = data.get("web", {})
        plus = web.get("plus", {})
        patron = web.get("patron", {})
        return SubscriptionStatus(
            paid=data.get("paid"),
            platform=data.get("platform"),
            auto_renewing=data.get("autoRenewing"),
            gift_days=data.get("giftDays"),
            cancel_url=data.get("cancelUrl"),
            update_url=data.get("updateUrl"),
            frequency=data.get("frequency"),
            web=(
                SubscriptionWeb(
                    monthly=web.get("monthly"),
                    yearly=web.get("yearly"),
                    trial=web.get("trial"),
                    web_status=web.get("webStatus"),
                    plus=(
                        SubscriptionTier(
                            monthly=plus.get("monthly"),
                            yearly=plus.get("yearly"),
                            trial_days=plus.get("trialDays"),
                        )
                        if plus
                        else None
                    ),
                    patron=(
                        SubscriptionTier(
                            monthly=patron.get("monthly"),
                            yearly=patron.get("yearly"),
                            trial_days=patron.get("trialDays"),
                        )
                        if patron
                        else None
                    ),
                )
                if web
                else None
            ),
            subscriptions=data.get("subscriptions"),
            type=data.get("type"),
            index=data.get("index"),
            web_status=data.get("webStatus"),
            tier=data.get("tier"),
            features=(
                SubscriptionFeatures(
                    remove_banner_ads=features.get("removeBannerAds"),
                    remove_discover_ads=features.get("removeDiscoverAds"),
                )
                if features
                else None
            ),
            created_at=data.get("createdAt"),
        )
    except httpx.HTTPStatusError as e:
        raise PocketCastsAuthError(
            message="Failed to fetch subscription status.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except Exception as e:
        raise PocketCastsAuthError(
            message="Unexpected error during subscription status fetch.",
            details={"exception": str(e)},
        )
