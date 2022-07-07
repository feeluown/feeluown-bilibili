import asyncio
import json
from typing import Type

import aiohttp

from fuo_bilibili.api.schema.enums import VideoQualityNum
from fuo_bilibili.api.schema.requests import BaseRequest, VideoInfoRequest, PlayUrlRequest
from fuo_bilibili.api.schema.responses import BaseResponse
from fuo_bilibili.api.video import VideoMixin
from fuo_bilibili.const import PLUGIN_API_COOKIEJAR_FILE


class BilibiliApi(VideoMixin):
    def __init__(self):
        self._cookie = aiohttp.CookieJar(unsafe=True)
        # self._load_cookie_from_file()
        self._session = aiohttp.ClientSession(cookie_jar=self._cookie)

    def _load_cookie_from_file(self):
        if PLUGIN_API_COOKIEJAR_FILE.exists():
            self._cookie.load(PLUGIN_API_COOKIEJAR_FILE)

    def _dump_cookie_to_file(self):
        self._cookie.save(PLUGIN_API_COOKIEJAR_FILE)

    async def get(self, url: str, param: BaseRequest, clazz: Type[BaseResponse]) -> BaseResponse:
        async with self._session.get(url, params=json.loads(param.json(exclude_none=True))) as r:
            response_dict = await r.text()
            return clazz.parse_raw(response_dict)

    async def close(self):
        try:
            # self._dump_cookie_to_file()
            await self._session.close()
        except Exception as e:
            print(f'Something is wrong when destroy api connection: {str(e)}')


async def main():
    api = BilibiliApi()
    info = await api.video_get_info(VideoInfoRequest(bvid='BV1qG411W76E'))
    data = info.data
    print(data)
    url_info = await api.video_get_url(PlayUrlRequest(
        bvid=data.bvid,
        cid=data.cid,
        qn=VideoQualityNum.q1080p60
    ))
    print(url_info.data)
    await api.close()


if __name__ == '__main__':
    asyncio.run(main())
