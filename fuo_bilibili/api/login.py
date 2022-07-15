from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, PasswordLoginRequest, SendSmsCodeRequest, \
    SmsCodeLoginRequest
from fuo_bilibili.api.schema.responses import BaseResponse, RequestCaptchaResponse, \
    RequestLoginKeyResponse, PasswordLoginResponse, SendSmsCodeResponse, SmsCodeLoginResponse


class LoginMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PASSPORT_BASE = 'https://passport.bilibili.com'

    def get_uncached(self, url: str, param: Optional[BaseRequest],
                     clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def get(self, url: str, param: Optional[BaseRequest],
            clazz: Union[Type[BaseResponse], Type[BaseModel], None]) -> Any:
        pass

    def post(self, url: str, param: Optional[BaseRequest], clazz: Type[BaseResponse], is_json=False, **kwargs) -> Any:
        pass

    def _dump_cookie_to_file(self):
        pass

    def request_captcha(self) -> RequestCaptchaResponse:
        url = f'{self.PASSPORT_BASE}/x/passport-login/captcha?source=main_web'
        return self.get_uncached(url, None, RequestCaptchaResponse)

    def request_login_key(self) -> RequestLoginKeyResponse:
        url = f'{self.PASSPORT_BASE}/login?act=getkey'
        response: RequestLoginKeyResponse = self.get_uncached(url, None, RequestLoginKeyResponse)
        # 接口没有状态码 pydantic 判断字段存在 根据字段是否空判断
        if response.key == '' or response.hash == '':
            raise RuntimeError('getkey error')
        return response

    def send_sms_code(self, request: SendSmsCodeRequest) -> SendSmsCodeResponse:
        url = f'{self.PASSPORT_BASE}/x/passport-login/web/sms/send'
        return self.post(url, request, SendSmsCodeResponse)

    def sms_code_login(self, request: SmsCodeLoginRequest) -> SmsCodeLoginResponse:
        url = f'{self.PASSPORT_BASE}/x/passport-login/web/login/sms'
        resp: SmsCodeLoginResponse = self.post(url, request, SmsCodeLoginResponse)
        if resp.data.url is not None:
            self.get_uncached(resp.data.url, None, None)
        self._dump_cookie_to_file()
        return resp

    def password_login(self, request: PasswordLoginRequest) -> PasswordLoginResponse:
        """
        账号密码登录
        """
        url = f'{self.PASSPORT_BASE}/x/passport-login/web/login'
        resp: PasswordLoginResponse = self.post(url, request, PasswordLoginResponse,
                                                headers={
                                                    'user-agent': 'Mozilla/5.0',
                                                    'referer': 'https://passport.bilibili.com/login',
                                                    'content-type': 'application/x-www-form-urlencoded'
                                                })
        if resp.data.status != 2:
            self._dump_cookie_to_file()
        return resp
