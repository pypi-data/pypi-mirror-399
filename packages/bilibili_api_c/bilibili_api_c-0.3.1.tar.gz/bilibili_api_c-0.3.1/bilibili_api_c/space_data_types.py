from typing import Optional
from dataclasses import dataclass


@dataclass
class SeriesVideoInfo:
    aid: int
    title: str
    pubdate: int
    ctime: int
    state: int
    pic: str
    duration: int
    stat: Optional[None]
    bvid: str
    ugc_pay: int
    interactive_video: bool
    enable_vt: int
    vt_display: str
    playback_position: int
    desc: str
    upMid: int
