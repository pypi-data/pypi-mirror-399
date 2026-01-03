from typing import Optional, Generator, List, Tuple
from enum import Enum

from .base import BaseClient
from .creative_center_data_types import BilibiliVideoDetailCreativeCenter, SectionEpisode, EpisodeSorts, SectionSorts
from .creative_center_response_types import GetSeasonResponse, GetSectionResponse, GetVideoResponse


class EpisodesSortMethod(Enum):
    PUBLISH_ASC = "asc"
    PUBLISH_DESC = "desc"
    AS_IS = "as_is"

class BilibiliCreativeCenter(BaseClient):
    def get_video_detail(self, aid: int) -> Optional[GetVideoResponse]:
        resp = self._get_request(url="https://member.bilibili.com/x/web/archive/videos", params={"aid": aid})
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return None

        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return None

        return GetVideoResponse(**resp_json["data"])

    def get_videos_by_page(self, page_number: int = 1) -> Optional[list[BilibiliVideoDetailCreativeCenter]]:
        resp = self._get_request(url="https://member.bilibili.com/x/web/archives",
                                 params={"status": "pubed", "pn": page_number, "ps": 10, "coop": 1, })
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return None

        try:
            response_json = resp.json()
        except ValueError:
            self.logger.error("unable to decode json")
            return None

        print(response_json)
        if response_json["code"] != 0:
            self.logger.error(f"got error code {response_json['code']} {response_json['message']}")
            return None

        if response_json["data"]["arc_audits"] is None:
            self.logger.error("arc_audits is null")
            return None

        return_list: list[BilibiliVideoDetailCreativeCenter] = []
        try:
            for each_video in response_json["data"]["arc_audits"]:
                # print(each_video)
                return_list.append(BilibiliVideoDetailCreativeCenter(
                    aid=each_video["Archive"]["aid"],
                    bvid=each_video["Archive"]["bvid"],
                    title=each_video["Archive"]["title"],
                    description=each_video["Archive"]["desc"],
                    tags=each_video["Archive"]["tag"],
                    duration=each_video["Archive"]["duration"],
                    copyright=each_video["Archive"]["copyright"],
                    source=each_video["Archive"]["source"],
                    ptime=each_video["Archive"]["ptime"],
                    ctime=each_video["Archive"]["ctime"],
                    zone_id=each_video["Archive"]["tid"],
                    zone_name=each_video["typename"],
                    subtitle_count=each_video["captions_count"],
                ))
            # END for
        except KeyError:
            self.logger.error("unable to find parse arc_audits (KeyError)")
            return None
        return return_list

    def get_videos_generator(self, page_limit: int = 10) -> Generator[BilibiliVideoDetailCreativeCenter, None, None]:
        """
        Get videos from the creative center

        :param page_limit: -1 for no limit
        :return:
        """
        current_page_number = 1
        while current_page_number <= page_limit or page_limit == -1:
            video_list = self.get_videos_by_page(page_number=current_page_number)
            if video_list is None:
                self.logger.error(f"Failed to get video list from page {current_page_number}")
                return
            for video in video_list:
                yield video
            # END for
            self.logger.info(f"Page {current_page_number} done")
            current_page_number += 1
        # END while

    def get_season_detail(self, season_id: int) -> Optional[GetSeasonResponse]:
        resp = self._get_request(url="https://member.bilibili.com/x2/creative/web/season", params={"id": season_id})
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return None
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return None

        return GetSeasonResponse(**resp.json())

    def get_section_detail(self, section_id: int) -> Optional[GetSectionResponse]:
        resp = self._get_request(url="https://member.bilibili.com/x2/creative/web/section", params={"id": section_id})
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return None
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return None

        return GetSectionResponse(**resp.json())

    def add_episodes_to_section(self, section_id: int, episodes: List[SectionEpisode]):
        resp = self._post_request(url="https://member.bilibili.com/x2/creative/web/season/section/episodes/add",
                                  params={"csrf": self.credential.csrf},
                                  data={
                                      "sectionId": section_id,
                                      "episodes": episodes,
                                  })
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return False, f"got status code {resp.status_code} from {resp.url}"
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return False, resp_json["message"]

    def submit_section_changes(self, section_detail: GetSectionResponse, sort: EpisodesSortMethod = EpisodesSortMethod.AS_IS) -> Tuple[bool, str]:
        episode_sorts: List[EpisodeSorts] = []
        match sort:
            case EpisodesSortMethod.AS_IS:
                for episode in section_detail.episodes:
                    episode_sorts.append(EpisodeSorts(id=episode.id, sort=episode.order))
            case EpisodesSortMethod.PUBLISH_ASC:
                section_detail.episodes.sort(key=lambda x: x.aid)
                for i, episode in enumerate(section_detail.episodes):
                    episode_sorts.append(EpisodeSorts(id=episode.id, sort=i+1))
            case EpisodesSortMethod.PUBLISH_DESC:
                section_detail.episodes.sort(key=lambda x: x.aid, reverse=True)
                for i, episode in enumerate(section_detail.episodes):
                    episode_sorts.append(EpisodeSorts(id=episode.id, sort=i+1))
            # END match
        # END match

        resp = self._post_request(url="https://member.bilibili.com/x2/creative/web/season/section/edit",
                                  params={"csrf": self.credential.csrf},
                                  data={
                                      "section": {
                                          "id": section_detail.section.id,
                                          "seasonId": section_detail.section.seasonId,
                                          "title": section_detail.section.title,
                                          "type": section_detail.section.type,
                                      }
                                  })
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return False, f"got status code {resp.status_code} from {resp.url}"
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return False, resp_json["message"]

        return True, "success"

    def submit_season_changes(self, season_detail: GetSeasonResponse) -> Tuple[bool, str]:
        section_sorts: List[SectionSorts] = []
        for section in season_detail.sections.sections:
            section_sorts.append(SectionSorts(id=section.id, sort=section.order))

        resp = self._post_request(url="https://member.bilibili.com/x2/creative/web/season/edit",
                                  params={"csrf": self.credential.csrf},
                                  data={
                                      "season": {
                                          "cover": season_detail.season.cover,
                                          "desc": season_detail.season.desc,
                                          "id": season_detail.season.id,
                                          "isEnd": season_detail.season.isEnd,
                                          "season_price": season_detail.season.season_price,
                                          "title": season_detail.season.title,
                                      },
                                      "sorts": section_sorts,
                                  })
        if resp.status_code >= 400:
            self.logger.error(f"got status code {resp.status_code} from {resp.url}")
            return False, f"got status code {resp.status_code} from {resp.url}"
        resp_json = resp.json()
        if resp_json["code"] != 0:
            self.logger.error(f"got error code {resp_json['code']} {resp_json['message']}")
            return False, resp_json["message"]

        return True, "success"

