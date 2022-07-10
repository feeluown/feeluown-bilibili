from typing import Type, Any

from fuo_bilibili.api.schema.requests import VideoInfoRequest, PlayUrlRequest, BaseRequest
from fuo_bilibili.api.schema.responses import VideoInfoResponse, PlayUrlResponse, BaseResponse


class VideoMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PLAYER_API_BASE = 'https://api.bilibili.com/x/player'

    def get(self, url: str, param: BaseRequest, clazz: Type[BaseResponse]) -> Any:
        pass

    def video_get_info(self, request: VideoInfoRequest) -> VideoInfoResponse:
        url = f'{self.API_BASE}/view'
        return self.get(url, request, VideoInfoResponse)

    def video_get_url(self, request: PlayUrlRequest) -> PlayUrlResponse:
        url = f'{self.PLAYER_API_BASE}/playurl'
        return self.get(url, request, PlayUrlResponse)
