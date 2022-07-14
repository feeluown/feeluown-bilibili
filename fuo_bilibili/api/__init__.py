import json
from http.cookiejar import MozillaCookieJar
from typing import Type, Optional, Union

import requests.cookies
from cachetools import LRUCache, cached
from pydantic import BaseModel

from fuo_bilibili.api.base import BaseMixin
from fuo_bilibili.api.login import LoginMixin
from fuo_bilibili.api.schema.enums import VideoQualityNum, SearchType
from fuo_bilibili.api.schema.requests import BaseRequest, VideoInfoRequest, PlayUrlRequest, SearchRequest
from fuo_bilibili.api.schema.responses import BaseResponse
from fuo_bilibili.api.video import VideoMixin
from fuo_bilibili.const import PLUGIN_API_COOKIEJAR_FILE

CACHE = LRUCache(10)


class BilibiliApi(BaseMixin, VideoMixin, LoginMixin):
    def __init__(self):
        self._cookie = MozillaCookieJar(PLUGIN_API_COOKIEJAR_FILE)
        self._session = requests.Session()
        self._session.cookies = self._cookie

    @staticmethod
    def cookie_check():
        if not PLUGIN_API_COOKIEJAR_FILE.exists():
            return False
        return True

    def load_cookies(self):
        self._cookie.load()

    def _dump_cookie_to_file(self):
        print('dumping cookies to file')
        self._cookie.save()

    @cached(CACHE)
    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None])\
            -> Union[BaseResponse, BaseModel, None]:
        print(f'Requesting: {url}...')
        if param is None:
            r = self._session.get(url)
            print(r.request.headers)
        else:
            r = self._session.get(url, params=json.loads(param.json(exclude_none=True)))
        print(r.text)
        if r.status_code != 200:
            raise RuntimeError('http not 200')
        if clazz is None:
            return None
        response_str = r.text
        res: Union[BaseResponse, BaseModel] = clazz.parse_raw(response_str)
        if isinstance(res, BaseResponse) and res.code != 0:
            raise RuntimeError(f'code not ok: {res.message}')
        return res

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs)\
            -> BaseResponse:
        if param is None:
            r = self._session.post(url, **kwargs)
        else:
            request = json.loads(param.json(exclude_none=True, by_alias=True))
            print(request)
            if is_json:
                r = self._session.post(url, json=request, **kwargs)
            else:
                r = self._session.post(url, data=request, **kwargs)
        if r.status_code != 200:
            print(r.request.headers, r.text)
            raise RuntimeError(f'http not 200: {r.status_code}')
        response_str = r.text
        print(json.loads(param.json(exclude_none=True, by_alias=True)), response_str)
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
    info = api.nav_info()
    print(info)
    api.close()


if __name__ == '__main__':
    main()
