from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import SearchRequest, BaseRequest
from fuo_bilibili.api.schema.responses import SearchResponse, BaseResponse, NavInfoResponse


class BaseMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PASSPORT_BASE = 'https://passport.bilibili.com'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    def _dump_cookie_to_file(self):
        pass

    def search(self, request: SearchRequest) -> SearchResponse:
        url = f'{self.API_BASE}/search/type'
        return self.get(url, request, SearchResponse)

    def nav_info(self) -> NavInfoResponse:
        url = f'{self.API_BASE}/nav'
        return self.get(url, None, NavInfoResponse)
