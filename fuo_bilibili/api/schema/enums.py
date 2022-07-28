from enum import Enum

from feeluown.media import Quality


class SearchType(Enum):
    """
    搜索目标类型
    """
    VIDEO = 'video'  # 视频
    BANGUMI = 'media_bangumi'  # 番剧
    MEDIA = 'media_ft'  # 影视
    LIVE = 'live'  # 直播间/主播
    LIVE_ROOM = 'live_room'  # 直播间
    LIVE_USER = 'live_user'  # 主播
    ARTICLE = 'article'  # 专栏文章
    TOPIC = 'topic'  # 话题
    BILI_USER = 'bili_user'  # 用户
    PHOTO = 'photo'  # 相册


class MediaType(Enum):
    bangumi = 1
    movie = 2
    document = 3
    national_creation = 4
    series = 5
    entertainment = 7


class UserType(Enum):
    """
    用户分类
    """
    ALL = 0
    UP = 1  # UP主
    NORMAL = 2
    VERIFIED = 3  # 认证用户


class VipType(Enum):
    """
    会员类型
    """
    NO = 0
    MONTH = 1  # 月度大会员
    YEAR = 2  # 年度大会员或以上


class VideoDurationType(Enum):
    """
    视频时长筛选
    """
    ALL = 0
    LT10 = 1
    GT10LT30 = 2
    GT30LT60 = 3
    GT60 = 4


class SearchOrderType(Enum):
    """
    搜索结果排序方式
    """
    # 视频、专栏、相册
    TOTALRANK = 'totalrank'  # 综合排序
    CLICK = 'click'  # 最多点击
    PUBDATE = 'pubdate'  # 最新发布
    DM = 'dm'  # 最多弹幕
    STOW = 'stow'  # 最多收藏
    SCORES = 'scores'  # 最多评论
    # 相册
    ATTENTION = 'attention'  # 最多喜欢
    # 直播间
    ONLINE = 'online'  # 人气直播
    LIVE_TIME = 'live_time'  # 最新开播
    # 用户
    USER_DEFAULT = '0'  # 默认排序
    FANS = 'fans'  # 粉丝数
    LEVEL = 'level'  # 用户等级


class VideoQualityNum(Enum):
    """
    视频清晰度
    """
    q240 = 6
    q360 = 16
    q480 = 32
    q720 = 64
    # 以下清晰度需要登录
    q720p60 = 74
    q1080 = 80
    # 以下清晰度一般需要登录大会员账号
    q1080p = 112
    q1080p60 = 116
    q4k = 120
    qhdr = 125  # HDR 真彩色
    qdolby = 126  # 杜比视界
    q8k = 127

    def get_quality(self) -> Quality.Video:
        if self.value >= 80:
            return Quality.Video.fhd
        if self.value >= 64:
            return Quality.Video.hd
        if self.value >= 32:
            return Quality.Video.sd
        return Quality.Video.ld

    @classmethod
    def get_max_from_quality(cls, quality: Quality.Video) -> int:
        match quality:
            case Quality.Video.fhd:
                return cls.q8k.value
            case Quality.Video.hd:
                return cls.q720p60.value
            case Quality.Video.sd:
                return cls.q480.value
        return cls.q360.value


class VideoFnval(Enum):
    """
    视频获取方式
    """
    DEFAULT = 0
    FLV = 2
    MP4 = 1  # 仅240P/360P 有限速
    DASH = 16  # Dash 音视频分流
    DASH_ALT = 80


class CodecId(Enum):
    """
    CodecId
    """
    AUDIO = 0
    AVC = 7
    HEVC = 12


class VideoCopyright(Enum):
    """
    视频类型原创或转载
    """
    ORIGIN = 1
    FORWARD = 2


class VideoState(Enum):
    PASSED = 1
    PUBLIC = 0
    PENDING_AUDIT = -1
    REJECTED = -2
    POLICE_LOCKED = -3
    LOCKED = -4
    ADMIN_LOCKED = -5
    FIXED_PENDING_AUDIT = -6
    TEMP_PAUSED_AUDIT = -7
    RESUBMIT_PENDING_AUDIT = -8
    PENDING_TRANSCODE = -9
    DELAYED_AUDIT = -10


class VideoFrom(Enum):
    VUPLOAD = 'vupload'  # 普通上传（B站）
    HUNAN = 'hunan'  # 芒果TV
    QQ = 'qq'  # 腾讯视频


class FavoriteResourceOrderType(Enum):
    MTIME = 'mtime'  # 最近收藏
    VIEW = 'view'  # 最多播放
    PUBTIME = 'pubtime'  # 最新投稿


class CommentType(Enum):
    video = 1  # 视频稿件
    topic = 2  # 话题
    activity = 3  # 活动
    audio = 14  # 音频
