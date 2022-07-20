from pydantic import BaseModel, Field

from fuo_bilibili.api.schema.enums import VideoQualityNum, VideoFnval, SearchType, SearchOrderType, UserType, \
    VideoDurationType, FavoriteResourceOrderType


class BaseRequest(BaseModel):
    def __hash__(self):
        return hash(self.json())


class GeetestBase(BaseModel):
    token: str
    challenge: str
    validate_: str = Field(alias='validate')
    seccode: str


class PaginatedRequest(BaseRequest):
    pn: int = 1  # 页码
    ps: int = 20  # 每页数量


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


class FavoriteListRequest(BaseRequest):
    up_mid: int  # UID
    type: int = 2  # 2:视频
    rid: int = None  # 资源ID


class CollectedFavoriteListRequest(PaginatedRequest):
    up_mid: int  # UID
    platform: str = 'web'


class FavoriteInfoRequest(BaseRequest):
    media_id: int  # 收藏夹ID


class FavoriteResourceRequest(PaginatedRequest):
    media_id: int  # 收藏夹ID
    keyword: str = None  # 关键词搜索
    order: FavoriteResourceOrderType = FavoriteResourceOrderType.MTIME  # 排序方式
    type: int = 0
    tid: int = 0


class FavoriteSeasonResourceRequest(PaginatedRequest):
    season_id: int  # 合集ID


class HomeRecommendVideosRequest(PaginatedRequest):
    refresh_type: int = 3
    version: int = 1
    fresh_idx: int = 2
    fresh_idx_1h: int = 2
    homepage_ver: int = 1


class HomeDynamicVideoRequest(BaseRequest):
    timezone_offset: int = -480
    type: str = 'video'
    offset: str = None
    page: int = 1


class UserInfoRequest(BaseRequest):
    mid: int  # 用户UID


class UserBestVideoRequest(BaseRequest):
    vmid: int


class UserVideoRequest(PaginatedRequest):
    mid: int
    order: str = None
    tid: int = None
    keyword: str = None
