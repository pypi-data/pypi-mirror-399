from typing import Optional, List
from dataclasses import dataclass

@dataclass
class VideoArchive:
    aid: int
    bvid: str
    title: str

@dataclass
class VideoPage:
    cid: int
    index: int
    title: str
    duration: int


@dataclass
class BilibiliVideoDetailCreativeCenter:
    bvid: str
    aid: int
    title: str
    description: str
    tags: list[str]
    duration: int
    copyright: int
    source: str
    zone_id: int  # tid
    zone_name: str  # typename
    subtitle_count: int
    # date related
    ptime: int
    ctime: int

@dataclass
class Season:
    id: int
    title: str
    desc: str
    cover: str
    isEnd: int
    mid: int
    isAct: int
    is_pay: int
    state: int
    partState: int
    signState: int
    rejectReason: str
    ctime: int
    mtime: int
    no_section: int
    forbid: int
    protocol_id: str
    ep_num: int
    season_price: int
    is_opened: int
    has_charging_pay: int
    has_pugv_pay: int
    SeasonUpfrom: int

@dataclass
class SectionSorts:
    id: int  # episode id
    sort: int

@dataclass
class Section:
    id: int
    type: int
    seasonId: int
    title: str
    order: int
    state: int
    partState: int
    rejectReason: str
    ctime: int
    mtime: int
    epCount: int
    cover: str
    has_charging_pay: int
    Episodes: Optional[None]
    show: int
    has_pugv_pay: int

@dataclass
class Sections:
    sections: List[Section]
    total: int

@dataclass
class EpisodeSorts:
    id: int  # episode id
    sort: int

@dataclass
class SectionEpisode:
    aid: int
    cid: int
    title: str
    charging_pay: int = 0
    member_first: int = 0


@dataclass
class SeasonEpisodeFullDetail:
    id: int
    title: str
    aid: int
    bvid: str
    cid: int
    seasonId: int
    sectionId: int
    order: int
    videoTitle: str
    archiveTitle: str
    archiveState: int
    rejectReason: str
    state: int
    cover: str
    is_free: int
    aid_owner: bool
    charging_pay: int
    member_first: int
    pugv_pay: int
