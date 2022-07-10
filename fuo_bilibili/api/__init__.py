import json
from typing import Type

import requests.cookies
from cachetools import LRUCache, cached

from fuo_bilibili.api.base import BaseMixin
from fuo_bilibili.api.schema.enums import VideoQualityNum, SearchType
from fuo_bilibili.api.schema.requests import BaseRequest, VideoInfoRequest, PlayUrlRequest, SearchRequest
from fuo_bilibili.api.schema.responses import BaseResponse
from fuo_bilibili.api.video import VideoMixin

CACHE = LRUCache(10)


class BilibiliApi(BaseMixin, VideoMixin):
    def __init__(self):
        self._cookie = requests.cookies.RequestsCookieJar()
        # self._load_cookie_from_file()
        self._session = requests.Session()
        self._session.cookies = self._cookie

    # todo: load cookie from file
    # def _load_cookie_from_file(self):
    #     if PLUGIN_API_COOKIEJAR_FILE.exists():
    #         self._cookie.load(PLUGIN_API_COOKIEJAR_FILE)
    #
    # def _dump_cookie_to_file(self):
    #     self._cookie.save(PLUGIN_API_COOKIEJAR_FILE)

    @cached(CACHE)
    def get(self, url: str, param: BaseRequest, clazz: Type[BaseResponse]) -> BaseResponse:
        print(f'Requesting: {url}...')
        r = self._session.get(url, params=json.loads(param.json(exclude_none=True)))
        if r.status_code != 200:
            raise RuntimeError('http not 200')
        response_str = r.text
        res: BaseResponse = clazz.parse_raw(response_str)
        if res.code != 0:
            raise RuntimeError(f'code not ok: {res.message}')
        return res

    def close(self):
        try:
            # self._dump_cookie_to_file()
            self._session.close()
        except Exception as e:
            print(f'Something is wrong when destroy api connection: {str(e)}')


def main():
    api = BilibiliApi()
    info = api.search(SearchRequest(
        search_type=SearchType.VIDEO,
        keyword='阿梓 舍离断'
    ))
    data = info.data
    print(data)
    api.close()


if __name__ == '__main__':
    main()
