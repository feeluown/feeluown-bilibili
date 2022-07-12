from datetime import datetime, timedelta
from typing import Any, List, Union

from pydantic import BaseModel, validator, Field

from fuo_bilibili.api.schema.enums import VideoQualityNum, CodecId, VideoCopyright, VideoState, VideoFrom, SearchType


class BaseResponse(BaseModel):
    code: int = None
    message: str = None
    ttl: int = None
    data: Any


class Dimension(BaseModel):
    width: int
    height: int
    rotate: int


class SearchResultVideo(BaseModel):
    type: SearchType
    id: int  # av号
    author: str  # UPer
    mid: int  # UID
    typeid: int  # 分区id
    typename: str  # 分区名称
    arcurl: str
    aid: int
    bvid: str  # bv号
    title: str  # 标题
    description: str  # 简介
    arcrank: str
    pic: str  # 视频封面
    play: int  # 播放量
    video_review: int  # 弹幕量
    favorites: int  # 收藏量
    tag: str  # 视频标签
    review: int  # 评论数
    pubdate: datetime
    senddate: datetime
    duration: timedelta
    badgepay: bool
    hit_columns: List[str]
    view_type: str
    is_pay: bool
    is_union_video: bool
    rank_score: int


class RequestCaptchaResponse(BaseResponse):
    class RequestCaptchaResponseData(BaseModel):
        class Geetest(BaseModel):
            gt: str
            challenge: str

        geetest: Geetest
        tencent: dict
        token: str
        type: str

    data: RequestCaptchaResponseData = None


class RequestLoginKeyResponse(BaseModel):
    hash: str
    key: str


class PasswordLoginResponse(BaseResponse):
    class PasswordLoginResponseData(BaseModel):
        status: int = None
        message: str = None
        url: str = None

    data: PasswordLoginResponseData = None


class SearchResponse(BaseResponse):
    class SearchResponseData(BaseModel):
        seid: int
        page: int
        pagesize: int  # 每页条数
        numResults: int  # 总数
        numPages: int  # 总页数
        suggest_keyword: str
        rqt_type: str
        cost_time: dict
        exp_list: dict = None
        egg_hit: int
        pageinfo: dict = None
        result: Union[List[Union[SearchResultVideo]], dict]  # 搜索结果 todo: obj
        show_column: int

    data: SearchResponseData = None


class VideoInfoResponse(BaseResponse):
    class VideoInfoResponseData(BaseModel):
        class DescV2(BaseModel):
            raw_text: str
            type: int
            biz_id: int = None

        class Rights(BaseModel):
            bp: int
            elec: bool  # 支持充电
            download: bool  # 允许下载
            movie: bool  # 是否是电影
            pay: bool  # 是否PGC付费
            hd5: bool  # 是否支持高码率
            no_reprint: bool  # 是否显示禁止转载
            autoplay: bool  # 是否自动播放
            ugc_pay: bool  # 是否UGC付费
            is_cooperation: bool  # 是否联合投稿
            ugc_pay_preview: bool  # UGC付费预览
            no_background: bool
            clean_mode: bool
            is_stein_gate: bool
            is_360: bool
            no_share: bool
            arc_pay: bool
            free_watch: bool

        class Owner(BaseModel):
            mid: int  # UID
            name: str  # 用户名
            face: str  # 头像

        class Stat(BaseModel):
            aid: int  # AV号
            view: int  # 播放量
            danmaku: int  # 弹幕量
            reply: int  # 评论量
            favorite: int  # 收藏量
            coin: int  # 投币量
            share: int  # 分享量
            now_rank: int  # 当前排名
            his_rank: int  # 历史最高排名
            like: int  # 点赞量
            dislike: int  # 点踩量
            evaluation: str  # 视频评分
            argue_msg: str  # 警告提示信息

        class Page(BaseModel):
            cid: int  # 分P cid
            page: int  # 当前分P
            from_: VideoFrom = Field(alias='from')  # 视频来源
            part: str  # 分P标题
            duration: timedelta
            vid: str = None  # 站外视频id
            weblink: str = None  # 站外视频链接
            dimension: Dimension

        class Subtitle(BaseModel):
            class SubtitleListItem(BaseModel):
                class Author(BaseModel):
                    mid: int  # 上传者UID
                    name: str  # 昵称
                    sex: str  # 性别
                    face: str  # 头像
                    sign: str  # 签名
                    rank: int
                    birthday: int
                    is_fake_account: bool
                    is_deleted: bool

                id: int
                lan: str  # 语言
                lan_doc: str  # 语言名
                is_lock: bool  # 是否锁定
                author_mid: int = None  # 上传者UID
                subtitle_url: str  # 字幕文件 json
                author: Author

            allow_submit: bool  # 是否允许提交字幕
            list: List[SubtitleListItem]

        class Staff(BaseModel):
            class Vip(BaseModel):
                type: int  # 会员类型 0：无 1：月会员 2：年会员
                status: bool
                theme_type: int

            mid: int  # UID
            title: str  # 成员名称
            name: str  # 成员昵称
            face: str  # 头像
            vip: Vip
            official: dict
            follower: int  # 粉丝数

        bvid: str
        aid: int
        videos: int  # 分P总数
        tid: int  # 分区id
        tname: str  # 子分区名称
        copyright: VideoCopyright
        pic: str  # 封面
        title: str  # 标题
        pubdate: datetime  # 稿件发布时间
        ctime: datetime  # 用户投稿时间
        desc: str  # 简介
        desc_v2: List[DescV2] = None  # 新版视频简介
        state: VideoState
        duration: timedelta
        forward: int = None
        mission_id: int = None
        redirect_url: str = None
        rights: Rights
        owner: Owner
        stat: Stat
        dynamic: str
        cid: int  # 1P cid
        dimension: Dimension
        no_cache: bool
        pages: List[Page]
        subtitle: Subtitle
        staff: List[Staff] = None
        user_garb: dict

    data: VideoInfoResponseData = None


class PlayUrlResponse(BaseResponse):
    class PlayUrlResponseData(BaseModel):
        class Durl(BaseModel):
            order: int
            length: timedelta  # 视频长度秒
            size: int  # 视频大小 Bytes
            url: str  # 视频流url
            backup_url: List[str] = None  # 备用视频流

            @classmethod
            @validator('length')
            def convert_ms(cls, v):
                return v / 1000

        class Dash(BaseModel):
            class DashItem(BaseModel):
                id: int  # 音视频清晰度代码
                base_url: str  # 默认视频/音频流
                backup_url: List[str] = None  # 备用视频/音频流
                bandwidth: int
                mime_type: str
                codecs: str
                width: int
                height: int
                frame_rate: str  # 视频帧率
                sar: str  # Sample Aspect Ratio
                start_with_sap: int  # Stream Access Point
                segment_base: dict
                codecid: CodecId

            duration: timedelta  # 视频长度秒
            video: List[DashItem]
            audio: List[DashItem]

        quality: VideoQualityNum
        format: str
        timelength: timedelta  # 视频长度毫秒
        accept_format: str  # 支持的格式
        accept_description: List[str]  # 支持的分辨率列表描述
        accept_quality: List[VideoQualityNum]  # 支持的分辨率代码列表
        durl: List[Durl] = None  # vlc/mp4 视频分段
        dash: Dash = None

        @classmethod
        @validator('timelength')
        def convert_ms(cls, v):
            return v / 1000

    data: PlayUrlResponseData = None
