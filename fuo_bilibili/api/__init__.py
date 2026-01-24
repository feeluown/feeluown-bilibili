import json
import logging
from datetime import timedelta
from http.cookiejar import MozillaCookieJar, CookieJar
from typing import Type, Optional, Union, List
from threading import Lock

import requests.cookies
from cachetools import TTLCache
from .compat import BaseModel

from fuo_bilibili.api.audio import AudioMixin
from fuo_bilibili.api.base import BaseMixin
from fuo_bilibili.api.history import HistoryMixin
from fuo_bilibili.api.live import LiveMixin
from fuo_bilibili.api.login import LoginMixin
from fuo_bilibili.api.media import MediaMixin
from fuo_bilibili.api.playlist import PlaylistMixin
from fuo_bilibili.api.schema.requests import *  # noqa
from fuo_bilibili.api.schema.responses import *  # noqa
from fuo_bilibili.api.user import UserMixin
from fuo_bilibili.api.video import VideoMixin
from fuo_bilibili.const import PLUGIN_API_COOKIEJAR_FILE
from .wbi import encWbi

CACHE = TTLCache(50, ttl=timedelta(minutes=10).total_seconds())
logger = logging.getLogger(__name__)


class BilibiliApi(BaseMixin, VideoMixin, LoginMixin, PlaylistMixin, HistoryMixin, UserMixin, AudioMixin, LiveMixin,
                  MediaMixin):
    TIMEOUT = 10

    def __init__(self):
        self._headers = {
            'Referer': 'https://www.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/33.0.1750.152 Safari/537.36'
        }
        self._session = requests.Session()
        # UPDATE(2024-01-11): To make self.nav_info work, the header needs to be added
        # UPDATE(2023-xx-xx): The header cause some API failing: self.nav_info
        self._session.headers.update(self._headers)
        self._wbi: Optional[NavInfoResponse.NavInfoResponseData.Wbi] = None

        # I guess the cookie is updated by the server periodically.
        # Update the cookie file, so that it is still valid when the app is restarted.
        # HACK: since feeluown has no mechanism to update the cookie file,
        # we save cookie every N successful requests to keep it updated :)
        self.enable_auto_save_cookie = True
        self._auto_save_cookie_counter = 0
        self._auto_save_cookie_lock = Lock()

    def maybe_save_cookie(self):
        from fuo_bilibili.login import dump_user_cookies

        need_save = False
        if self.enable_auto_save_cookie:
            with self._auto_save_cookie_lock:
                self._auto_save_cookie_counter += 1
                if self._auto_save_cookie_counter >= 20:
                    need_save = True
                    self._auto_save_cookie_counter = 0
        if need_save is True:
            logger.info("auto save cookie")
            cookiedict = dict(self.get_cookiejar())
            dump_user_cookies(cookiedict)

    def get_session(self):
        return self._session

    def get_cookiejar(self):
        return self._session.cookies

    def from_cookiedict(self, cookies):
        cookiejar = requests.cookies.cookiejar_from_dict(cookies)
        self._session.cookies = cookiejar

    def set_wbi(self, wbi: NavInfoResponse.NavInfoResponseData.Wbi):
        self._wbi = wbi

    @staticmethod
    def clear_cache_by_url(urls: List[str]):
        for key in CACHE.keys():
            if len(key) < 2:
                continue
            url = key[1]
            if url in urls:
                CACHE.pop(key)

    def _get_csrf(self):
        for cookie in self.get_cookiejar():
            if cookie.name == 'bili_jct':
                return cookie.value
        raise RuntimeError('bili_jct not found')

    def get_uncached(self, url: str, param: Optional[BaseRequest],
                     clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) \
            -> Union[BaseResponse, BaseModel, None]:
        if param is None:
            r = self._session.get(url, timeout=self.TIMEOUT, **kwargs)
        else:
            def handle_base_request_param(param: BaseRequest):
                return json.loads(param.json(exclude_none=True))

            def handle_base_wbi_request_param(param: BaseWbiRequest):
                img_key = self._wbi.img_url.rsplit('/', 1)[1].split('.')[0]
                sub_key = self._wbi.sub_url.rsplit('/', 1)[1].split('.')[0]
                js = json.loads(param.json(exclude_none=True))
                return encWbi(js, img_key, sub_key)

            if isinstance(param, BaseCsrfRequest):
                param.csrf = self._get_csrf()
                js = json.loads(param.json(exclude_none=True))
            elif isinstance(param, BaseOptionalWbiRequest):
                if self._wbi is not None:
                    js = handle_base_wbi_request_param(param)
                else:
                    js = handle_base_request_param(param)
            elif isinstance(param, BaseWbiRequest):
                if self._wbi is None:
                    raise RuntimeError('wbi info is empty (not logged in)')
                js = handle_base_wbi_request_param(param)
            else:
                js = handle_base_request_param(param)
            r = self._session.get(url, timeout=self.TIMEOUT,
                                  params=js,
                                  **kwargs)
        if r.status_code != 200:
            print(r.text)
            raise RuntimeError('http not 200')
        if clazz is None:
            return None
        response_str = r.text
        logger.debug(f'api response body: {response_str}')
        res: Union[BaseResponse, BaseModel] = clazz.parse_raw(response_str)
        if isinstance(res, BaseResponse) and res.code != 0:
            raise RuntimeError(f'code not ok: {res}, url:{url}, param:{param}')
        self.maybe_save_cookie()
        return res

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None],
            **kwargs) \
            -> Union[BaseResponse, BaseModel, None]:
        return self.get_uncached(url, param, clazz, **kwargs)

    def get_content(self, url: str) -> str:
        return self._session.get(url).text

    def get_content_raw(self, url: str) -> bytes:
        return self._session.get(url).content

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) \
            -> BaseResponse:
        if param is None:
            r = self._session.post(url, timeout=self.TIMEOUT, **kwargs)
        else:
            if isinstance(param, BaseCsrfRequest):
                param.csrf = self._get_csrf()
            request = json.loads(param.json(exclude_none=True, by_alias=True))
            if is_json:
                r = self._session.post(url, timeout=self.TIMEOUT, json=request, **kwargs)
            else:
                r = self._session.post(url, timeout=self.TIMEOUT, data=request, **kwargs)
        if r.status_code != 200:
            raise RuntimeError(f'http not 200: {r.status_code}')
        response_str = r.text
        res = clazz.parse_raw(response_str)
        if res.code != 0:
            raise RuntimeError(f'code not ok: {res.code} {res.message}')
        self.maybe_save_cookie()
        return res

    def close(self):
        try:
            self._session.close()
        except Exception as e:
            print(f'Something is wrong when destroy api connection: {str(e)}')


def main():
    from fuo_bilibili.login import load_user_cookies
    api = BilibiliApi()
    cookiedict = load_user_cookies()
    api.from_cookiedict(cookiedict)
    # info = api.history_later_videos()
    # info = api.history_add_later_videos(HistoryAddLaterVideosRequest(bvid='BV1RN4y1j7k6'))
    # info = api.video_get_info(VideoInfoRequest(bvid='BV1wnSYBQE4y'))
    # print(info)
    data = api.nav_info().data
    api.set_wbi(data.wbi_img)
    r = api.video_get_url(PlayUrlRequest(
        bvid='BV1wnSYBQE4y',
        cid=34471741344,
        fnval=VideoFnval.DASH
    ))
    print(r.data.dash.flac['audio']['baseUrl'])
    api.close()


if __name__ == '__main__':
    main()
