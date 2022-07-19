from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import SearchRequest, BaseRequest, PaginatedRequest, HomeRecommendVideosRequest, \
    HomeDynamicVideoRequest
from fuo_bilibili.api.schema.responses import SearchResponse, BaseResponse, NavInfoResponse, \
    HomeRecommendVideosResponse, HomeDynamicVideoResponse


class BaseMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PASSPORT_BASE = 'https://passport.bilibili.com'
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def search(self, request: SearchRequest) -> SearchResponse:
        url = f'{self.API_BASE}/search/type'
        return self.get(url, request, SearchResponse)

    def nav_info(self) -> NavInfoResponse:
        url = f'{self.API_BASE}/nav'
        return self.get(url, None, NavInfoResponse)

    def home_recommend_videos(self, request: HomeRecommendVideosRequest) -> HomeRecommendVideosResponse:
        url = f'{self.API_BASE}/index/top/rcmd'
        return self.get_uncached(url, request, HomeRecommendVideosResponse)

    def home_dynamic_videos(self, request: HomeDynamicVideoRequest) -> HomeDynamicVideoResponse:
        url = f'{self.APIX_BASE}/polymer/web-dynamic/v1/feed/all'
        return self.get_uncached(url, request, HomeDynamicVideoResponse)
