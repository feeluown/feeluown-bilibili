from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, MediaGetListRequest, MediaFavlistRequest
from fuo_bilibili.api.schema.responses import BaseResponse, MediaGetListResponse, MediaFavlistResponse


class MediaMixin:
    API_PGC_BASE = 'https://api.bilibili.com/pgc'
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def media_bangumi_get_list(self, request: MediaGetListRequest) -> MediaGetListResponse:
        url = f'{self.API_PGC_BASE}/view/web/season'
        return self.get(url, request, MediaGetListResponse)

    def media_bangumi_favlist(self, request: MediaFavlistRequest) -> MediaFavlistResponse:
        url = f'{self.APIX_BASE}/space/bangumi/follow/list'
        return self.get(url, request, MediaFavlistResponse)
