from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, AnotherPaginatedRequest, LivePlayUrlRequest
from fuo_bilibili.api.schema.responses import BaseResponse, LiveFeedListResponse, LivePlayUrlResponse


class LiveMixin:
    API_LIVE_BASE = 'https://api.live.bilibili.com'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    def live_feed_list(self, request: AnotherPaginatedRequest) -> LiveFeedListResponse:
        url = f'{self.API_LIVE_BASE}/relation/v1/feed/feed_list'
        return self.get(url, request, LiveFeedListResponse)

    def live_play_url(self, request: LivePlayUrlRequest) -> LivePlayUrlResponse:
        url = f'{self.API_LIVE_BASE}/room/v1/Room/playUrl'
        return self.get(url, request, LivePlayUrlResponse)
