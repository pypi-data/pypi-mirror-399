from typing import List, Tuple
from dataclasses import dataclass

from .base import BaseClient, PaginationData
from .space_data_types import SeriesVideoInfo


class BilibiliSpace(BaseClient):
    def get_relevant_videos_for_series(self, mid: int, series_id: int, keywords: str = "") -> List[SeriesVideoInfo]:
        resp = self._get_request(url="https://api.bilibili.com/x/series/recArchivesByKeywords", params={"mid": mid, "keywords": keywords, "series_id": series_id})
        if resp.status_code >= 400:
            return []
        resp_json = resp.json()
        if resp_json["code"] != 0:
            return []
        return [SeriesVideoInfo(**video) for video in resp_json["data"]["archives"]]

    def add_video_to_series(self, series_id: int, aid_list: List[int]) -> Tuple[bool, str]:
        resp = self._post_request(url="https://api.bilibili.com/x/series/series/addArchives",
                                  params={"csrf": self.credential.csrf},
                                  data={
                                      "mid": self.credential.uid,
                                      "series_id": series_id,
                                      "aids": ",".join(map(lambda x: str(x), aid_list)),
                                  })
        if resp.status_code >= 400:
            self.logger.error(f"Failed to add video to series, status code {resp.status_code}")
            return False, f"Failed to add video to series, status code {resp.status_code}"
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"Failed to add video to series, response {resp_json['message']}")
            return False, resp_json["message"]
        return True, ""


@dataclass
class GetRelevantVideoForSeriesResponse:
    archives: List[SeriesVideoInfo]
    page: PaginationData