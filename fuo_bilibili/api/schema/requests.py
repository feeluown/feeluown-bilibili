from pydantic import BaseModel

from fuo_bilibili.api.schema.enums import VideoQualityNum, VideoFnval


class BaseRequest(BaseModel):
    pass


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
