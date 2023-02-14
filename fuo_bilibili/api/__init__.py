import json
from datetime import timedelta
from http.cookiejar import MozillaCookieJar
from typing import Type, Optional, Union, List

import requests.cookies
from cachetools import TTLCache, cached
from pydantic import BaseModel

from fuo_bilibili.api.audio import AudioMixin
from fuo_bilibili.api.base import BaseMixin
from fuo_bilibili.api.history import HistoryMixin
from fuo_bilibili.api.live import LiveMixin
from fuo_bilibili.api.login import LoginMixin
from fuo_bilibili.api.media import MediaMixin
from fuo_bilibili.api.playlist import PlaylistMixin
from fuo_bilibili.api.schema.enums import VideoQualityNum, SearchType
from fuo_bilibili.api.schema.requests import BaseRequest, VideoInfoRequest, PlayUrlRequest, SearchRequest, \
    FavoriteListRequest, PaginatedRequest, AudioFavoriteSongsRequest, AnotherPaginatedRequest, LivePlayUrlRequest, \
    MediaFavlistRequest, HistoryAddLaterVideosRequest, BaseCsrfRequest, HistoryDelLaterVideosRequest, \
    UserFollowingRequest
from fuo_bilibili.api.schema.responses import BaseResponse
from fuo_bilibili.api.user import UserMixin
from fuo_bilibili.api.video import VideoMixin
from fuo_bilibili.const import PLUGIN_API_COOKIEJAR_FILE, DANMAKU_DIRECTORY

CACHE = TTLCache(50, ttl=timedelta(minutes=10).total_seconds())


class BilibiliApi(BaseMixin, VideoMixin, LoginMixin, PlaylistMixin, HistoryMixin, UserMixin, AudioMixin, LiveMixin,
                  MediaMixin):
    TIMEOUT = 10

    def __init__(self):
        self._cookie = MozillaCookieJar(PLUGIN_API_COOKIEJAR_FILE)
        self._session = requests.Session()
        self._session.cookies = self._cookie

    @staticmethod
    def cookie_check():
        if not PLUGIN_API_COOKIEJAR_FILE.exists():
            return False
        return True

    @staticmethod
    def remove_cookie():
        PLUGIN_API_COOKIEJAR_FILE.unlink(missing_ok=True)

    def load_cookies(self):
        self._cookie.load()

    def _dump_cookie_to_file(self):
        print('dumping cookies to file')
        self._cookie.save()

    @staticmethod
    def clear_cache_by_url(urls: List[str]):
        for key in CACHE.keys():
            if len(key) < 2:
                continue
            url = key[1]
            if url in urls:
                CACHE.pop(key)

    def _get_csrf(self):
        for cookie in self._cookie:
            if cookie.name == 'bili_jct':
                return cookie.value
        raise RuntimeError('bili_jct not found')

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) \
            -> Union[BaseResponse, BaseModel, None]:
        print(f'Requesting: {url}...')
        if param is None:
            r = self._session.get(url, timeout=self.TIMEOUT, **kwargs)
        else:
            r = self._session.get(url, timeout=self.TIMEOUT, params=json.loads(param.json(exclude_none=True)), **kwargs)
        if r.status_code != 200:
            print(r.text)
            raise RuntimeError('http not 200')
        if clazz is None:
            return None
        response_str = r.text
        res: Union[BaseResponse, BaseModel] = clazz.parse_raw(response_str)
        if isinstance(res, BaseResponse) and res.code != 0:
            raise RuntimeError(f'code not ok: {res.message}')
        return res

    @cached(CACHE)
    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs)\
            -> Union[BaseResponse, BaseModel, None]:
        return self.get_uncached(url, param, clazz, **kwargs)

    @cached(CACHE)
    def get_content(self, url: str) -> str:
        return self._session.get(url).text

    @cached(CACHE)
    def get_content_raw(self, url: str) -> bytes:
        return self._session.get(url).content

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs)\
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
        return res

    def close(self):
        try:
            self._session.close()
        except Exception as e:
            print(f'Something is wrong when destroy api connection: {str(e)}')


def main():
    api = BilibiliApi()
    api.load_cookies()
    # info = api.history_later_videos()
    # info = api.history_add_later_videos(HistoryAddLaterVideosRequest(bvid='BV1RN4y1j7k6'))
    info = api.video_weekly_list()
    print(info.json())
    api.close()


if __name__ == '__main__':
    main()
