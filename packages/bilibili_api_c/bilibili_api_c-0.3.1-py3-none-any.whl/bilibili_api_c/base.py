from typing import Union
from dataclasses import dataclass
import logging
import os

import requests


REQUEST_HEADERS = {
    "Referer": "https://www.bilibili.com/",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 30

class BilibiliCredential:
    def __init__(self,
                 uid: Union[str, int],
                 sessdata: str, csrf: str,
                 username: str = None, password: str = None,
                 buvid3: str = None, access_token: str = None):
        self.uid: str = str(uid)
        self.username = username
        self.password = password
        self.sessdata = sessdata
        self.csrf = csrf
        self.buvid3 = buvid3
        self.access_token = access_token

    @staticmethod
    def init_from_env(raise_if_invalid: bool = True):
        print("Initializing credential from environment variables: BILIBILI_UID, BILIBILI_SESSDATA, BILIBILI_CSRF")
        instance = BilibiliCredential(uid=os.environ.get("BILIBILI_UID"), sessdata=os.environ.get("BILIBILI_SESSDATA"), csrf=os.environ.get("BILIBILI_CSRF"))
        if raise_if_invalid and not instance.validate():
            raise ValueError("Invalid credential")
        return instance

    @staticmethod
    def is_not_empty(input_value: str) -> bool:
        return input_value is not None and input_value != ""

    def get_cookie(self) -> dict:
        return_dict = {}
        if self.is_not_empty(self.sessdata):
            return_dict["SESSDATA"] = self.sessdata
        if self.is_not_empty(self.csrf):
            return_dict["bili_jct"] = self.csrf
        if self.is_not_empty(self.buvid3):
            return_dict["buvid3"] = self.buvid3
        return return_dict

    def get_cookie_for_url(self, url: str) -> dict:
        if url.find(".bilibili.com") >= 0:
            return self.get_cookie()
        else:
            return {}

    def validate(self) -> bool:
        print("Validating credential...")
        resp = requests.get("https://space.bilibili.com/", headers=REQUEST_HEADERS, cookies=self.get_cookie())
        print(resp.status_code, resp.url)
        if (resp.url == "https://passport.bilibili.com/login?gourl=https://space.bilibili.com"
                or resp.url == "https://passport.bilibili.com/pc/passport/login?gourl=https%3A%2F%2Fspace.bilibili.com"):  # will try to redirect to login page if SESSDATA is expired
            print("bilibili.com credential not valid", self.get_cookie())
            return False
        print("bilibili.com credential valid")
        return True

class BaseClient:
    def __init__(self, credential: BilibiliCredential,
                 logger: logging.Logger = logging.getLogger("bilibili_api_c")
                 ):
        self.credential = credential
        self.requests_session = requests.Session()
        self.logger = logger

    def _get_request(self, url: str, params: dict, use_credential: bool = True) -> requests.Response:
        return self.requests_session.get(url=url, params=params, cookies=self.credential.get_cookie_for_url(url) if use_credential else {}, headers=REQUEST_HEADERS)

    def _post_request(self, url: str, params: dict, data: dict, use_credential: bool = True) -> requests.Response:
        return self.requests_session.post(url=url, params=params, data=data, cookies=self.credential.get_cookie_for_url(url) if use_credential else {}, headers=REQUEST_HEADERS)


@dataclass
class PaginationData:
    num: int
    size: int
    total: int