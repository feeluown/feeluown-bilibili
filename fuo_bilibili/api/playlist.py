from typing import Type, Any, Optional, Union, List

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, FavoriteListRequest, FavoriteInfoRequest, \
    FavoriteResourceRequest, CollectedFavoriteListRequest, FavoriteSeasonResourceRequest, \
    FavoriteResourceOperateRequest, FavoriteNewRequest
from fuo_bilibili.api.schema.responses import BaseResponse, FavoriteListResponse, FavoriteInfoResponse, \
    FavoriteResourceResponse, CollectedFavoriteListResponse, FavoriteSeasonResourceResponse


class PlaylistMixin:
    """收藏夹接口"""
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    @staticmethod
    def clear_cache_by_url(urls: List[str]):
        pass

    def favorite_list(self, request: FavoriteListRequest) -> FavoriteListResponse:
        url = f'{self.APIX_BASE}/v3/fav/folder/created/list-all'
        return self.get(url, request, FavoriteListResponse)

    def collected_favorite_list(self, request: CollectedFavoriteListRequest) -> CollectedFavoriteListResponse:
        url = f'{self.APIX_BASE}/v3/fav/folder/collected/list'
        return self.get(url, request, CollectedFavoriteListResponse)

    def favorite_info(self, request: FavoriteInfoRequest) -> FavoriteInfoResponse:
        url = f'{self.APIX_BASE}/v3/fav/folder/info'
        return self.get(url, request, FavoriteInfoResponse)

    def favorite_resource(self, request: FavoriteResourceRequest) -> FavoriteResourceResponse:
        url = f'{self.APIX_BASE}/v3/fav/resource/list'
        return self.get(url, request, FavoriteResourceResponse)

    def favorite_season_resource(self, request: FavoriteSeasonResourceRequest) -> FavoriteSeasonResourceResponse:
        url = f'{self.APIX_BASE}/space/fav/season/list'
        return self.get(url, request, FavoriteSeasonResourceResponse)

    def favorite_resource_operate(self, request: FavoriteResourceOperateRequest) -> BaseResponse:
        url = f'{self.APIX_BASE}/v3/fav/resource/deal'
        return self.post(url, request, BaseResponse)

    def favorite_new(self, request: FavoriteNewRequest) -> BaseResponse:
        url = f'{self.APIX_BASE}/v3/fav/folder/add'
        self.clear_cache_by_url([f'{self.APIX_BASE}/v3/fav/folder/created/list-all'])
        return self.post(url, request, BaseResponse)
