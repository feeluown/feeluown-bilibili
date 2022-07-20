from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, UserInfoRequest, UserBestVideoRequest, UserVideoRequest
from fuo_bilibili.api.schema.responses import BaseResponse, UserInfoResponse, UserBestVideoResponse, UserVideoResponse


class UserMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PASSPORT_BASE = 'https://passport.bilibili.com'
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def user_info(self, param: UserInfoRequest) -> UserInfoResponse:
        url = f'{self.APIX_BASE}/space/acc/info'
        return self.get_uncached(url, param, UserInfoResponse, headers={
            'user-agent': 'Mozilla/5.0',
            'referer': 'https://www.bilibili.com',
        })

    def user_best_videos(self, request: UserBestVideoRequest) -> UserBestVideoResponse:
        url = f'{self.APIX_BASE}/space/masterpiece'
        return self.get(url, request, UserBestVideoResponse)

    def user_videos(self, request: UserVideoRequest) -> UserVideoResponse:
        url = f'{self.APIX_BASE}/space/arc/search'
        return self.get(url, request, UserVideoResponse)
