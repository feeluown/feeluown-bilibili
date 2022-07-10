from typing import Type, Any

from fuo_bilibili.api.schema.requests import SearchRequest, BaseRequest
from fuo_bilibili.api.schema.responses import SearchResponse, BaseResponse


class BaseMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'

    def get(self, url: str, param: BaseRequest, clazz: Type[BaseResponse]) -> Any:
        pass

    def search(self, request: SearchRequest) -> SearchResponse:
        url = f'{self.API_BASE}/search/type'
        return self.get(url, request, SearchResponse)
