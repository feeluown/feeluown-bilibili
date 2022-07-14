from pydantic import BaseModel, Field

from fuo_bilibili.api.schema.enums import VideoQualityNum, VideoFnval, SearchType, SearchOrderType, UserType, \
    VideoDurationType


class BaseRequest(BaseModel):
    def __hash__(self):
        return hash(self.json())


class GeetestBase(BaseModel):
    token: str
    challenge: str
    validate_: str = Field(alias='validate')
    seccode: str


class SendSmsCodeRequest(BaseRequest, GeetestBase):
    tel: str  # 手机号（不包含国家代码）
    cid: str = '+86'  # 国家代码
    source: str = 'main_web'


class SmsCodeLoginRequest(BaseRequest):
    tel: str  # 手机号（不包含国家代码）
    cid: str = '+86'  # 国家代码
    code: str  # 验证码
    source: str = 'main_web'
    captcha_key: str
    keep: bool = True


class PasswordLoginRequest(BaseRequest, GeetestBase):
    source: str = 'main_h5'
    username: str
    password: str  # 加密后密码
    keep: bool = True


class SearchRequest(BaseRequest):
    search_type: SearchType
    keyword: str
    order: SearchOrderType = None
    order_sort: int = None  # 用户粉丝数及等级排序顺序 1:升序 0:降序(default)
    user_type: UserType = None
    duration: VideoDurationType = None
    tids: int = None  # 视频分区
    category_id: int = None  # 专栏分区 todo enum
    page: int = None  # 分页


class VideoInfoRequest(BaseRequest):
    aid: int = None
    bvid: str


class PlayUrlRequest(BaseRequest):
    avid: int = None
    bvid: str
    cid: int
    qn: VideoQualityNum = None
    fnval: VideoFnval = None
    fnver: int = 0
    fourk: int = None  # 是否允许4K视频
    otype: str = 'json'
    platform: str = 'pc'
