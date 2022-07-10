from pydantic import BaseModel

from fuo_bilibili.api.schema.enums import VideoQualityNum, VideoFnval, SearchType, SearchOrderType, UserType, \
    VideoDurationType


class BaseRequest(BaseModel):
    def __hash__(self):
        return hash(self.json())


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
