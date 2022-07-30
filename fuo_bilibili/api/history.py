from typing import Type, Any, Optional, Union, List

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, PaginatedRequest, HistoryAddLaterVideosRequest, \
    HistoryDelLaterVideosRequest
from fuo_bilibili.api.schema.responses import BaseResponse, HistoryLaterVideoResponse, HistoryVideoResponse


class HistoryMixin:
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    @staticmethod
    def clear_cache_by_url(urls: List[str]):
        pass

    def history_later_videos(self) -> HistoryLaterVideoResponse:
        url = f'{self.APIX_BASE}/v2/history/toview'
        return self.get(url, None, HistoryLaterVideoResponse)

    def history_videos(self, request: PaginatedRequest) -> HistoryVideoResponse:
        url = f'{self.APIX_BASE}/v2/history'
        return self.get(url, request, HistoryVideoResponse)

    def history_add_later_videos(self, request: HistoryAddLaterVideosRequest) -> BaseResponse:
        url = f'{self.APIX_BASE}/v2/history/toview/add'
        self.clear_cache_by_url([f'{self.APIX_BASE}/v2/history/toview'])
        return self.post(url, request, BaseResponse)

    def history_del_later_videos(self, request: HistoryDelLaterVideosRequest) -> BaseResponse:
        url = f'{self.APIX_BASE}/v2/history/toview/del'
        self.clear_cache_by_url([f'{self.APIX_BASE}/v2/history/toview'])
        return self.post(url, request, BaseResponse)
