"""
Pocket Casts API synchronous client orchestrator.

This module provides the PocketCastsClient class, which acts as a thin orchestrator:
- All endpoint logic is delegated to stateless functions in the endpoints/ subpackage.
- This class manages only in-memory user/session state and access token.
- No authentication, subscription, or API logic is implemented here directly.

Usage:
    client = PocketCastsClient()
    user = client.login_pocket_casts(email, password)
    podcasts = client.get_subscribed_podcasts()
    client.subscribe_to_podcast(podcast_uuid)
    client.unsubscribe_from_podcast(podcast_uuid)
"""

from api_pocketcasts.models import User


class PocketCastsClient:

    def __init__(self):
        self._access_token = None
        self._user = None

    def login_pocket_casts(self, email: str, password: str) -> User:
        """
        Log in to Pocket Casts and return a User object.
        Thin orchestrator: delegates to endpoints.auth.login_pocket_casts.
        """
        from api_pocketcasts.endpoints.auth import login_pocket_casts

        user = login_pocket_casts(email, password)
        self._access_token = user.access_token
        self._user = user
        return user

    def refresh_token(self, refresh_token: str) -> User:
        """
        Refresh the Pocket Casts access token using the /user/token endpoint.
        Thin orchestrator: delegates to endpoints.auth.refresh_token.
        Updates self._access_token and self._user on success.
        """
        from api_pocketcasts.endpoints.auth import refresh_token as refresh_token_func

        user = refresh_token_func(refresh_token)
        self._access_token = user.access_token
        self._user = user
        return user

    def get_subscribed_podcasts(self):
        """
        Retrieve the list of podcasts the user is subscribed to.
        Thin orchestrator: delegates to endpoints.podcasts.get_subscribed_podcasts.
        """
        from api_pocketcasts.endpoints.podcasts import get_subscribed_podcasts

        return get_subscribed_podcasts(self._access_token)

    def subscribe_to_podcast(self, podcast_uuid: str):
        """
        Subscribe the user to a podcast.
        Thin orchestrator: delegates to endpoints.podcasts.subscribe_to_podcast.
        """
        from api_pocketcasts.endpoints.podcasts import subscribe_to_podcast

        return subscribe_to_podcast(self._access_token, podcast_uuid)

    def unsubscribe_from_podcast(self, podcast_uuid: str):
        """
        Unsubscribe the user from a podcast.
        Thin orchestrator: delegates to endpoints.podcasts.unsubscribe_from_podcast.
        """
        from api_pocketcasts.endpoints.podcasts import unsubscribe_from_podcast

        return unsubscribe_from_podcast(self._access_token, podcast_uuid)

    def get_podcast_full(self, podcast_uuid: str):
        """
        Fetch full podcast details, including all episodes, using GET /podcast/full/{podcast_uuid}.
        Thin orchestrator: delegates to endpoints.podcasts.get_podcast_full.
        """
        from api_pocketcasts.endpoints.podcasts import get_podcast_full

        return get_podcast_full(podcast_uuid)
