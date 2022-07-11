import json
from http.cookiejar import MozillaCookieJar
from typing import Type, Optional, Union

import requests.cookies
from cachetools import LRUCache, cached
from pydantic import BaseModel

from fuo_bilibili.api.base import BaseMixin
from fuo_bilibili.api.schema.enums import VideoQualityNum, SearchType
from fuo_bilibili.api.schema.requests import BaseRequest, VideoInfoRequest, PlayUrlRequest, SearchRequest
from fuo_bilibili.api.schema.responses import BaseResponse
from fuo_bilibili.api.video import VideoMixin
from fuo_bilibili.const import PLUGIN_API_COOKIEJAR_FILE

CACHE = LRUCache(10)


class BilibiliApi(BaseMixin, VideoMixin):
    def __init__(self):
        self._cookie = MozillaCookieJar(PLUGIN_API_COOKIEJAR_FILE)
        self._session = requests.Session()
        self._session.cookies = self._cookie

    def _dump_cookie_to_file(self):
        print('dumping cookies to file')
        self._cookie.save()

    @cached(CACHE)
    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel]])\
            -> Union[BaseResponse, BaseModel]:
        print(f'Requesting: {url}...')
        if param is None:
            r = self._session.get(url)
        else:
            r = self._session.get(url, params=json.loads(param.json(exclude_none=True)))
        if r.status_code != 200:
            print(r.text)
            raise RuntimeError('http not 200')
        response_str = r.text
        res: Union[BaseResponse, BaseModel] = clazz.parse_raw(response_str)
        if isinstance(res, BaseResponse) and res.code != 0:
            raise RuntimeError(f'code not ok: {res.message}')
        return res

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_form=False, **kwargs)\
            -> BaseResponse:
        if param is None:
            request = None
            r = self._session.post(url, **kwargs)
        else:
            request = json.loads(param.json(exclude_none=True, by_alias=True))
            if is_form:
                r = self._session.post(url, data=request, **kwargs)
            else:
                r = self._session.post(url, json=request, **kwargs)
        if r.status_code != 200:
            print(r.text)
            raise RuntimeError('http not 200')
        response_str = r.text
        print(json.loads(param.json(exclude_none=True, by_alias=True)), response_str)
        res = clazz.parse_raw(response_str)
        if res.code != 0:
            raise RuntimeError(f'code not ok: {res.message}')
        return res

    def close(self):
        try:
            self._dump_cookie_to_file()
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
