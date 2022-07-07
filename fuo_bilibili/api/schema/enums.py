from enum import Enum


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
