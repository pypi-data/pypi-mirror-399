"""
Podcast, subscription, and show notes data models for Pocket Casts API.

Models included:
    - PodcastSetting, PodcastSettings
    - Podcast, PodcastList, PodcastFull
    - SubscriptionResult
    - MobileShowNotesFullTranscript
    - MobileShowNotesFullEpisode
    - MobileShowNotesFullPodcast
    - MobileShowNotesFullResponse
"""

import attr
from typing import List, Optional, Dict, Any


@attr.s(auto_attribs=True, frozen=True)
class PodcastSetting:
    value: Optional[Any] = None
    changed: Optional[bool] = None
    modifiedAt: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class PodcastSettings:
    notification: Optional[PodcastSetting] = None
    addToUpNext: Optional[PodcastSetting] = None
    addToUpNextPosition: Optional[PodcastSetting] = None
    autoArchive: Optional[PodcastSetting] = None
    playbackEffects: Optional[PodcastSetting] = None
    playbackSpeed: Optional[PodcastSetting] = None
    trimSilence: Optional[PodcastSetting] = None
    volumeBoost: Optional[PodcastSetting] = None
    autoStartFrom: Optional[PodcastSetting] = None
    autoSkipLast: Optional[PodcastSetting] = None
    episodesSortOrder: Optional[PodcastSetting] = None
    autoArchivePlayed: Optional[PodcastSetting] = None
    autoArchiveInactive: Optional[PodcastSetting] = None
    autoArchiveEpisodeLimit: Optional[PodcastSetting] = None
    episodeGrouping: Optional[PodcastSetting] = None
    showArchived: Optional[PodcastSetting] = None


@attr.s(auto_attribs=True, frozen=True)
class Podcast:
    uuid: str
    title: str
    author: str
    episodesSortOrder: Optional[int] = None
    autoStartFrom: Optional[int] = None
    description: Optional[str] = None
    url: Optional[str] = None
    lastEpisodePublished: Optional[str] = None
    unplayed: Optional[bool] = None
    lastEpisodeUuid: Optional[str] = None
    lastEpisodePlayingStatus: Optional[int] = None
    lastEpisodeArchived: Optional[bool] = None
    autoSkipLast: Optional[int] = None
    folderUuid: Optional[str] = None
    sortPosition: Optional[int] = None
    dateAdded: Optional[str] = None
    settings: Optional[PodcastSettings] = None
    descriptionHtml: Optional[str] = None
    isPrivate: Optional[bool] = None
    slug: Optional[str] = None


# New model for /podcast/full/{uuid} endpoint
@attr.s(auto_attribs=True, frozen=True)
class PodcastFull:
    episode_frequency: Optional[str] = None
    estimated_next_episode_at: Optional[str] = None
    has_seasons: Optional[bool] = None
    season_count: Optional[int] = None
    episode_count: Optional[int] = None
    has_more_episodes: Optional[bool] = None
    podcast: Optional[Dict[str, Any]] = None
    episodes: Optional[List[Any]] = None


@attr.s(auto_attribs=True, frozen=True)
class PodcastList:
    podcasts: List[Podcast]
    folders: Optional[List[Dict[str, Any]]] = None


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionResult:
    success: bool
    message: Optional[str] = None
    podcast_uuid: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class MobileShowNotesFullTranscript:
    url: str
    type: str


@attr.s(auto_attribs=True, frozen=True)
class MobileShowNotesFullEpisode:
    uuid: str
    title: str
    url: str
    published: str
    show_notes: str
    hash: str
    modified: int
    transcripts: List[Any]
    pocket_casts_transcripts: List[Any]
    image: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class MobileShowNotesFullPodcast:
    uuid: str
    episodes: List[MobileShowNotesFullEpisode]


@attr.s(auto_attribs=True, frozen=True)
class MobileShowNotesFullResponse:
    podcast: MobileShowNotesFullPodcast
