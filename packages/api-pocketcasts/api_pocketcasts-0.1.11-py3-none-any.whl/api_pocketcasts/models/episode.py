"""
Episode data model for Pocket Casts API (UserEpisode and related endpoints).
"""

import attr
from typing import Optional, List


@attr.s(auto_attribs=True, frozen=True)
class UserEpisode:
    """Represents a user episode entity as returned by POST /user/episode."""

    uuid: str
    url: Optional[str] = None
    published: Optional[str] = None  # ISO datetime
    duration: Optional[int] = None
    file_type: Optional[str] = None
    title: Optional[str] = None
    size: Optional[str] = None
    playing_status: Optional[int] = None
    played_up_to: Optional[int] = None
    starred: Optional[bool] = None
    podcast_uuid: Optional[str] = None
    podcast_title: Optional[str] = None
    episode_type: Optional[str] = None
    episode_season: Optional[int] = None
    episode_number: Optional[int] = None
    is_deleted: Optional[bool] = None
    author: Optional[str] = None
    bookmarks: Optional[List[dict]] = None
    podcast_slug: Optional[str] = None
    slug: Optional[str] = None

    # Note: 404 error responses for this endpoint are empty/non-JSON (see data-model.md)
