from typing import Optional, List
from dataclasses import dataclass

from .creative_center_data_types import Season, Sections, Section, SeasonEpisodeFullDetail, VideoArchive, VideoPage


@dataclass
class GetVideoResponse:
    archive: VideoArchive
    videos: List[VideoPage]

@dataclass
class GetSeasonResponse:
    season: Season
    course: Optional[None]
    checkin: Optional[None]
    seasonStat: Optional[None]
    sections: Sections
    part_episodes: Optional[List[SeasonEpisodeFullDetail]]

@dataclass
class GetSectionResponse:
    section: Section
    episodes: Optional[List[SeasonEpisodeFullDetail]]