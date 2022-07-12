from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import SearchRequest, BaseRequest, PasswordLoginRequest
from fuo_bilibili.api.schema.responses import SearchResponse, BaseResponse, RequestCaptchaResponse, \
    RequestLoginKeyResponse, PasswordLoginResponse


class BaseMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PASSPORT_BASE = 'https://passport.bilibili.com'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel]]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_form=False, **kwargs) -> Any:
        pass

    def search(self, request: SearchRequest) -> SearchResponse:
        url = f'{self.API_BASE}/search/type'
        return self.get(url, request, SearchResponse)

    def request_captcha(self) -> RequestCaptchaResponse:
        url = f'{self.PASSPORT_BASE}/x/passport-login/captcha?source=main_web'
        return self.get(url, None, RequestCaptchaResponse)

    def request_login_key(self) -> RequestLoginKeyResponse:
        url = f'{self.PASSPORT_BASE}/login?act=getkey'
        response: RequestLoginKeyResponse = self.get(url, None, RequestLoginKeyResponse)
        # 接口没有状态码 pydantic 判断字段存在 根据字段是否空判断
        if response.key == '' or response.hash == '':
            raise RuntimeError('getkey error')
        return response

    def password_login(self, request: PasswordLoginRequest) -> PasswordLoginResponse:
        """
        账号密码登录
        """
        url = f'{self.PASSPORT_BASE}/x/passport-login/web/login'
        return self.post(url, request, PasswordLoginResponse, is_form=True,
                         headers={
                             'user-agent': 'Mozilla/5.0',
                             'referer': 'https://passport.bilibili.com/login',
                             'content-type': 'application/x-www-form-urlencoded'
                         })
