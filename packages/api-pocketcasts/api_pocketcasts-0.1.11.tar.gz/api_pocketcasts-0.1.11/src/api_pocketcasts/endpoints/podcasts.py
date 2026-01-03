# Pocket Casts API endpoints: podcast subscriptions, metadata, and show notes.
#
# This module provides stateless, in-memory-only functions for:
#   - Listing user podcast subscriptions
#   - Subscribing/unsubscribing to podcasts
#   - Fetching user episode details
#   - Fetching full podcast metadata (with all episodes)
#   - Fetching public show notes and episode HTML for a podcast
#
# No credentials or tokens are ever persisted to disk.
#
# Functions:
#   - get_subscribed_podcasts
#   - subscribe_to_podcast
#   - unsubscribe_from_podcast
#   - get_user_episode
#   - get_podcast_full
#   - get_mobile_show_notes_full


import httpx
from typing import Dict, List, Optional, Any
from api_pocketcasts.models import (
    PodcastList,
    Podcast,
    PodcastSettings,
    PodcastSetting,
    SubscriptionResult,
    UserEpisode,
    MobileShowNotesFullResponse,
)

from api_pocketcasts.exceptions import (
    PocketCastsAuthError,
    PocketCastsAPIError,
    PocketCastsAPIResponseError,
)


def get_subscribed_podcasts(access_token: str) -> PodcastList:
    """
    Retrieve the list of podcasts the user is subscribed to.
    """
    PODCAST_LIST_URL: str = "https://api.pocketcasts.com/user/podcast/list"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers: Dict[str, str] = {"Authorization": f"Bearer {access_token}"}
    try:
        response: httpx.Response = httpx.post(
            PODCAST_LIST_URL,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        try:
            data: Dict[str, Any] = response.json()
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Failed to parse podcast list response as JSON.",
                details={"exception": str(e), "response": response.text},
            )
        if not isinstance(data, dict) or "podcasts" not in data:
            raise PocketCastsAPIResponseError(
                message="Podcast list response missing 'podcasts' field.",
                details={"response": data},
            )
        podcasts: List[Podcast] = []
        for p in data.get("podcasts", []):
            p = p  # type: ignore
            settings: Optional[PodcastSettings] = None
            if "settings" in p:
                try:
                    settings_kwargs: Dict[str, Any] = {}
                    for k, v in p["settings"].items():
                        settings_kwargs[k] = (
                            PodcastSetting(**v) if isinstance(v, dict) else None
                        )
                    settings = PodcastSettings(**settings_kwargs)  # type: ignore
                except Exception as e:
                    raise PocketCastsAPIResponseError(
                        message="Malformed PodcastSettings in podcast list response.",
                        details={
                            "exception": str(e),
                            "settings": p.get("settings"),
                        },
                    )
            try:
                podcasts.append(
                    Podcast(
                        uuid=p["uuid"],
                        episodesSortOrder=p.get("episodesSortOrder"),
                        autoStartFrom=p.get("autoStartFrom"),
                        title=p["title"],
                        author=p["author"],
                        description=p.get("description"),
                        url=p.get("url"),
                        lastEpisodePublished=p.get("lastEpisodePublished"),
                        unplayed=p.get("unplayed"),
                        lastEpisodeUuid=p.get("lastEpisodeUuid"),
                        lastEpisodePlayingStatus=p.get("lastEpisodePlayingStatus"),
                        lastEpisodeArchived=p.get("lastEpisodeArchived"),
                        autoSkipLast=p.get("autoSkipLast"),
                        folderUuid=p.get("folderUuid"),
                        sortPosition=p.get("sortPosition"),
                        dateAdded=p.get("dateAdded"),
                        settings=settings,
                        descriptionHtml=p.get("descriptionHtml"),
                        isPrivate=p.get("isPrivate"),
                        slug=p.get("slug"),
                    )
                )
            except Exception as e:
                raise PocketCastsAPIResponseError(
                    message="Malformed Podcast object in podcast list response.",
                    details={"exception": str(e), "podcast": p},
                )
        return PodcastList(podcasts=podcasts, folders=data.get("folders"))
    except PocketCastsAPIError:
        raise
    except httpx.HTTPStatusError as e:
        raise PocketCastsAuthError(
            message="Failed to fetch podcast list.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching podcast list.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching podcast list.",
            details={"exception": str(e)},
        )
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during podcast list fetch.",
            details={"exception": str(e)},
        )


def subscribe_to_podcast(access_token: str, podcast_uuid: str) -> SubscriptionResult:
    """
    Subscribe the user to a podcast.
    """
    PODCAST_SUBSCRIBE_URL = "https://api.pocketcasts.com/user/podcast/subscribe"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            PODCAST_SUBSCRIBE_URL,
            headers=headers,
            json={"uuid": podcast_uuid},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return SubscriptionResult(
            success=True, message=data.get("message"), podcast_uuid=podcast_uuid
        )
    except httpx.HTTPStatusError as e:
        return SubscriptionResult(
            success=False,
            message=f"Failed to subscribe: {e.response.text}",
            podcast_uuid=podcast_uuid,
        )
    except Exception as e:
        return SubscriptionResult(
            success=False,
            message=f"Unexpected error: {str(e)}",
            podcast_uuid=podcast_uuid,
        )


def unsubscribe_from_podcast(
    access_token: str, podcast_uuid: str
) -> SubscriptionResult:
    """
    Unsubscribe the user from a podcast.
    """
    PODCAST_UNSUBSCRIBE_URL = "https://api.pocketcasts.com/user/podcast/unsubscribe"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            PODCAST_UNSUBSCRIBE_URL,
            headers=headers,
            json={"uuid": podcast_uuid},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return SubscriptionResult(
            success=True, message=data.get("message"), podcast_uuid=podcast_uuid
        )
    except httpx.HTTPStatusError as e:
        return SubscriptionResult(
            success=False,
            message=f"Failed to unsubscribe: {e.response.text}",
            podcast_uuid=podcast_uuid,
        )
    except Exception as e:
        return SubscriptionResult(
            success=False,
            message=f"Unexpected error: {str(e)}",
            podcast_uuid=podcast_uuid,
        )


def get_user_episode(access_token: str, episode_uuid: str) -> UserEpisode:
    """
    Retrieve a single episode's details for the user (POST /user/episode).
    Raises PocketCastsAuthError for missing/invalid token,
        and PocketCastsAPIResponseError for 404 or malformed responses.
    """
    USER_EPISODE_URL = "https://api.pocketcasts.com/user/episode"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    if not episode_uuid:
        raise PocketCastsAPIResponseError(
            message="No episode UUID provided.",
            details={"episode_uuid": episode_uuid},
        )
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            USER_EPISODE_URL,
            headers=headers,
            json={"uuid": episode_uuid},
            timeout=10,
        )
        if response.status_code == 404:
            raise PocketCastsAPIResponseError(
                message="Episode not found (404).",
                details={
                    "status_code": 404,
                    "episode_uuid": episode_uuid,
                    "response": response.text,
                },
            )
        response.raise_for_status()
        try:
            data = response.json()
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Failed to parse user episode response as JSON.",
                details={"exception": str(e), "response": response.text},
            )
        # Strict validation of required fields and types
        required_fields = [
            ("uuid", str),
            ("url", str),
            ("published", str),
            ("duration", int),
            ("fileType", str),
            ("title", str),
            ("podcastUuid", str),
        ]
        for field, typ in required_fields:
            if field not in data or not isinstance(data[field], typ):
                raise PocketCastsAPIResponseError(
                    message=(
                        f"UserEpisode response missing or invalid type for required field '"
                        f"{field}'"
                    ),
                    details={
                        "field": field,
                        "expected_type": typ.__name__,
                        "data": data,
                    },
                )
        try:
            return UserEpisode(
                uuid=data["uuid"],
                url=data.get("url"),
                published=data.get("published"),
                duration=data.get("duration"),
                file_type=data.get("fileType"),
                title=data.get("title"),
                size=data.get("size"),
                playing_status=data.get("playingStatus"),
                played_up_to=data.get("playedUpTo"),
                starred=data.get("starred"),
                podcast_uuid=data.get("podcastUuid"),
                podcast_title=data.get("podcastTitle"),
                episode_type=data.get("episodeType"),
                episode_season=data.get("episodeSeason"),
                episode_number=data.get("episodeNumber"),
                is_deleted=data.get("isDeleted"),
                author=data.get("author"),
                bookmarks=data.get("bookmarks"),
                podcast_slug=data.get("podcastSlug"),
                slug=data.get("slug"),
            )
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Malformed UserEpisode object in response.",
                details={"exception": str(e), "data": data},
            )
    except httpx.HTTPStatusError as e:
        raise PocketCastsAPIError(
            code="http_error",
            message="HTTP error while fetching user episode.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching user episode.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching user episode.",
            details={"exception": str(e)},
        )
    except PocketCastsAPIError:
        raise
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during user episode fetch.",
            details={"exception": str(e)},
        )


def get_podcast_full(podcast_uuid: str, access_token: str = None) -> Podcast:
    """
    Fetch full podcast details, including all episodes, using GET /podcast/full/{podcast_uuid}.
    Optionally uses a Bearer token if provided.
    """
    PODCAST_FULL_URL = (
        f"https://podcast-api.pocketcasts.com/podcast/full/{podcast_uuid}"
    )
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    try:
        response = httpx.get(
            PODCAST_FULL_URL, headers=headers, timeout=10, follow_redirects=True
        )
        response.raise_for_status()
        data = response.json()
        # Validate required fields: only 'podcast' is required at the top level
        if not isinstance(data, dict) or "podcast" not in data:
            raise PocketCastsAPIResponseError(
                message="Podcast full response missing required 'podcast' field.",
                details={"response": data},
            )
        # Extract episodes from within the podcast object
        podcast_obj = data["podcast"]
        episodes = podcast_obj.get("episodes", [])
        from api_pocketcasts.models.podcast import PodcastFull

        podcast_full = PodcastFull(
            episode_frequency=data.get("episode_frequency"),
            estimated_next_episode_at=data.get("estimated_next_episode_at"),
            has_seasons=data.get("has_seasons"),
            season_count=data.get("season_count"),
            episode_count=data.get("episode_count"),
            has_more_episodes=data.get("has_more_episodes"),
            podcast=podcast_obj,
            episodes=episodes,
        )
        return podcast_full
    except Exception as e:
        raise PocketCastsAPIResponseError(
            message="Malformed Podcast object in podcast full response.",
            details={"exception": str(e), "data": data if "data" in locals() else None},
        )
    except httpx.HTTPStatusError as e:
        raise PocketCastsAPIError(
            code="http_error",
            message="HTTP error while fetching podcast full details.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching podcast full details.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching podcast full details.",
            details={"exception": str(e)},
        )
    except PocketCastsAPIError:
        raise
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during podcast full fetch.",
            details={"exception": str(e)},
        )


def get_mobile_show_notes_full(podcast_uuid: str) -> "MobileShowNotesFullResponse":
    """
    Fetch show notes and episode metadata for a podcast using
    GET /mobile/show_notes/full/{podcast_uuid}.
    Returns a MobileShowNotesFullResponse model.
    """
    import httpx
    from api_pocketcasts.models import (
        MobileShowNotesFullPodcast,
        MobileShowNotesFullEpisode,
        MobileShowNotesFullResponse,
    )
    from api_pocketcasts.exceptions import (
        PocketCastsAPIResponseError,
        PocketCastsAPIError,
    )

    SHOW_NOTES_URL = (
        f"https://podcast-api.pocketcasts.com/mobile/show_notes/full/{podcast_uuid}"
    )
    try:
        response = httpx.get(SHOW_NOTES_URL, timeout=10, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or "podcast" not in data:
            raise PocketCastsAPIResponseError(
                message="Show notes response missing required 'podcast' field.",
                details={"response": data},
            )
        podcast_obj = data["podcast"]
        # Validate podcast fields
        uuid = podcast_obj.get("uuid")
        episodes = podcast_obj.get("episodes", [])
        # Build episode models (optional: strict field mapping)
        episode_models = []
        for ep in episodes:
            episode_models.append(
                MobileShowNotesFullEpisode(
                    uuid=ep.get("uuid"),
                    title=ep.get("title"),
                    url=ep.get("url"),
                    published=ep.get("published"),
                    show_notes=ep.get("show_notes"),
                    hash=ep.get("hash"),
                    modified=ep.get("modified"),
                    image=ep.get("image"),
                    transcripts=ep.get("transcripts", []),
                    pocket_casts_transcripts=ep.get("pocket_casts_transcripts", []),
                )
            )
        podcast_model = MobileShowNotesFullPodcast(uuid=uuid, episodes=episode_models)
        return MobileShowNotesFullResponse(podcast=podcast_model)
    except Exception as e:
        raise PocketCastsAPIResponseError(
            message="Malformed response from show notes endpoint.",
            details={"exception": str(e)},
        )
    except httpx.HTTPStatusError as e:
        raise PocketCastsAPIError(
            code="http_error",
            message="HTTP error while fetching show notes.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching show notes.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching show notes.",
            details={"exception": str(e)},
        )
    except PocketCastsAPIError:
        raise
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during show notes fetch.",
            details={"exception": str(e)},
        )
