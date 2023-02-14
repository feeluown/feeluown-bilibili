from datetime import datetime, timedelta
from typing import Any, List, Union

from pydantic import BaseModel, validator, Field

from fuo_bilibili.api.schema.enums import VideoQualityNum, CodecId, VideoCopyright, VideoState, VideoFrom, SearchType, \
    VipType, MediaType


class BaseResponse(BaseModel):
    code: int = None
    message: str = None
    ttl: int = None
    data: Any


class Dimension(BaseModel):
    width: int
    height: int
    rotate: int


class Upper(BaseModel):
    mid: int
    name: str
    face: str = ''
    followed: bool = None
    vip_type: VipType = None
    vip_statue: bool = None


class CntInfo(BaseModel):
    collect: int
    play: int
    danmaku: int = None


class Owner(BaseModel):
    mid: int  # UID
    name: str  # 用户名
    face: str  # 头像


class Stat(BaseModel):
    aid: int = None  # AV号
    view: int  # 播放量
    danmaku: int  # 弹幕量
    reply: int = None  # 评论量
    favorite: int = None  # 收藏量
    coin: int = None  # 投币量
    share: int = None  # 分享量
    now_rank: int = None  # 当前排名
    his_rank: int = None  # 历史最高排名
    like: int  # 点赞量
    dislike: int = None  # 点踩量
    evaluation: str = None  # 视频评分
    argue_msg: str = None  # 警告提示信息


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
    clean_mode: bool = None
    is_stein_gate: bool = None
    is_360: bool = None
    no_share: bool = None
    arc_pay: bool
    free_watch: bool = None


class SearchResultUser(BaseModel):
    type: SearchType = SearchType.BILI_USER
    mid: int
    uname: str
    usign: str
    fans: int
    videos: int
    upic: str


class SearchResultMedia(BaseModel):
    class MediaScore(BaseModel):
        user_count: int
        score: float

    type: SearchType = SearchType.MEDIA
    media_id: int  # mdid
    season_id: int  # ssid
    title: str
    org_title: str
    cover: str
    media_type: MediaType
    areas: str
    styles: str
    cv: str
    staff: str
    desc: str
    corner: int
    media_score: MediaScore = None
    season_type_name: str
    is_follow: bool


class SearchResultLiveRoom(BaseModel):
    type: SearchType = SearchType.LIVE_ROOM
    uid: int
    tags: str  # 直播间tag
    live_time: datetime
    cate_name: str  # 子分区名
    live_status: bool
    uname: str
    uface: str
    user_cover: str  # 封面
    short_id: str  # 直播间短号
    title: str  # 标题
    cover: str  # 直播关键帧
    online: int  # 在线人数
    roomid: int  # 直播间id
    attentions: int  # 粉丝数


class SearchResultVideo(BaseModel):
    type: SearchType = SearchType.VIDEO
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


class SendSmsCodeResponse(BaseResponse):
    class SendSmsCodeResponseData(BaseModel):
        captcha_key: str

    data: SendSmsCodeResponseData = None


class PasswordLoginResponse(BaseResponse):
    class PasswordLoginResponseData(BaseModel):
        status: int = None
        message: str = None
        url: str = None

    data: PasswordLoginResponseData = None


class SmsCodeLoginResponse(BaseResponse):
    class SmsCodeLoginResponseData(BaseModel):
        url: str

    data: SmsCodeLoginResponseData = None


class NavInfoResponse(BaseResponse):
    class NavInfoResponseData(BaseModel):
        class LevelInfo(BaseModel):
            current_level: int
            current_min: int
            current_exp: int
            next_exp: str

        class VipLabel(BaseModel):
            text: str

        class Wallet(BaseModel):
            bcoin_balance: int  # B币
            coupon_balance: int  # 赠送B币数

        isLogin: bool
        email_verified: bool = None
        face: str = None
        mid: int = None  # UID
        mobile_verified: bool = None
        money: int = None  # 硬币数
        moral: int = None  # 节操值
        uname: str = None
        vipDueDate: datetime = None
        vipStatus: bool = None
        vipType: VipType = None
        vip_pay_type: bool = None
        wallet: Wallet = None
        level_info: LevelInfo = None
        vip_label: VipLabel = None

        @classmethod
        @validator('vipDueDate')
        def convert_ms(cls, v):
            return v / 1000

    data: NavInfoResponseData = None


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
        result: Union[List[Union[SearchResultVideo, SearchResultUser,
                                 SearchResultLiveRoom, SearchResultMedia]], dict] = None
        show_column: int

    data: SearchResponseData = None


class VideoInfoResponse(BaseResponse):
    class VideoInfoResponseData(BaseModel):
        class DescV2(BaseModel):
            raw_text: str
            type: int
            biz_id: int = None

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


class FavoriteListResponse(BaseResponse):
    class FavoriteListResponseData(BaseModel):
        class FavoriteList(BaseModel):
            id: int  # 收藏id
            fid: int  # 原始收藏夹id
            mid: int  # 创建者UID
            attr: int
            title: str  # 收藏夹标题
            fav_state: bool
            media_count: int  # 收藏夹内容数量
            type: int = 11

        count: int  # 总数
        list: List[FavoriteList]  # 收藏列表

    data: FavoriteListResponseData = None


class CollectedFavoriteListResponse(BaseResponse):
    class CollectedFavoriteListResponseData(BaseModel):
        class CollectedFavoriteList(BaseModel):
            id: int  # 收藏id
            fid: int  # 原始收藏夹id
            mid: int  # 创建者UID
            attr: int
            title: str  # 收藏夹标题
            fav_state: bool
            media_count: int  # 收藏夹内容数量
            cover: str  # 封面
            cover_type: int
            intro: str  # 简介
            link: str
            mtime: datetime
            state: int
            type: int  # 11: 分P 21: 合集
            upper: Upper
            view_count: int  # 总播放

        count: int  # 总数
        list: List[CollectedFavoriteList]  # 收藏列表

    data: CollectedFavoriteListResponseData = None


class FavoriteInfoResponse(BaseResponse):
    class FavoriteInfoResponseData(BaseModel):
        id: int
        fid: int
        mid: int
        attr: int
        title: str  # 标题
        cover: str  # 封面
        upper: Upper  # 创建者信息
        type: int  # 11: 分P 21: 合集
        intro: str  # 备注
        fav_state: bool  # 是否收藏
        like_state: bool  # 是否点赞
        media_count: int  # 收藏夹的内容数量

    data: FavoriteInfoResponseData = None


class FavoriteResourceResponse(BaseResponse):
    class FavoriteResourceResponseData(BaseModel):
        class Media(BaseModel):
            id: int
            type: int
            title: str
            cover: str
            intro: str
            page: int
            duration: timedelta
            upper: Upper
            cnt_info: CntInfo
            link: str  # 视频 deeplink
            # ctime: datetime
            # pubtime: datetime
            # favtime: datetime
            bvid: str

        medias: List[Media] = None

    data: FavoriteResourceResponseData = None


class FavoriteSeasonResourceResponse(BaseResponse):
    class FavoriteSeasonResourceResponseData(BaseModel):
        class Info(BaseModel):
            cnt_info: CntInfo
            cover: str
            id: int
            media_count: int
            season_type: int
            title: str
            upper: Upper

        class Media(BaseModel):
            id: int
            title: str
            cover: str
            duration: timedelta
            upper: Upper
            cnt_info: CntInfo
            # ctime: datetime
            # pubtime: datetime
            # favtime: datetime
            bvid: str

        info: Info
        medias: List[Media] = None

    data: FavoriteSeasonResourceResponseData = None


class HistoryLaterVideoResponse(BaseResponse):
    class HistoryLaterVideoResponseData(BaseModel):
        class LaterItem(BaseModel):
            aid: int
            videos: int  # 分P总数
            tid: int  # 分区
            tname: str  # 分区名
            copyright: VideoCopyright
            pic: str  # 封面
            title: str  # 标题
            desc: str  # 简介
            state: VideoState
            duration: timedelta
            rights: Rights
            owner: Owner
            stat: Stat
            dynamic: str  # 同步动态内容
            dimension: Dimension
            count: int = None  # 分P数
            cid: int  # cid
            progress: timedelta  # 观看进度
            bvid: str

        count: int
        list: List[LaterItem] = None

    data: HistoryLaterVideoResponseData = None


class HistoryVideoResponse(BaseResponse):
    class HistoryVideoResponseData(BaseModel):
        aid: int
        videos: int  # 分P总数
        tid: int  # 分区
        tname: str  # 分区名
        copyright: VideoCopyright
        pic: str  # 封面
        title: str  # 标题
        desc: str  # 简介
        state: VideoState
        duration: timedelta
        rights: Rights
        owner: Owner
        stat: Stat
        dynamic: str  # 同步动态内容
        dimension: Dimension
        cid: int  # cid
        favorite: bool
        type: int
        sub_type: int
        device: int
        count: int = None  # 分P数
        progress: timedelta  # 观看进度
        bvid: str

    data: List[HistoryVideoResponseData] = None


class HomeRecommendVideosResponse(BaseResponse):
    class HomeRecommendVideosResponseData(BaseModel):
        class Video(BaseModel):
            bvid: str
            cid: int
            duration: timedelta
            id: int
            is_followed: bool
            owner: Owner
            pic: str
            rcmd_reason: dict = None
            stat: Stat
            title: str
            uri: str

        item: List[Video]

    data: HomeRecommendVideosResponseData = None


class HomeDynamicVideoResponse(BaseResponse):
    class HomeDynamicVideoResponseData(BaseModel):
        class DynamicVideoItem(BaseModel):
            class Modules(BaseModel):
                class ModuleDynamic(BaseModel):
                    class Major(BaseModel):
                        class Archive(BaseModel):
                            aid: int
                            bvid: str
                            cover: str
                            desc: str
                            duration_text: str
                            title: str
                        archive: Archive
                    major: Major

                class ModuleAuthor(BaseModel):
                    mid: int
                    name: str
                    face: str

                module_dynamic: ModuleDynamic
                module_author: ModuleAuthor
            modules: Modules
        has_more: bool
        offset: str
        items: List[DynamicVideoItem]

    data: HomeDynamicVideoResponseData = None


class UserInfoResponse(BaseResponse):
    class UserInfoResponseData(BaseModel):
        class FansMedal(BaseModel):
            class Medal(BaseModel):
                target_id: int  # 勋章对应UP的UID
                medal_name: str  # 粉丝勋章名称
                level: int  # 等级
                medal_color: int

            show: bool
            wear: bool
            medal: Medal = None

        mid: int
        name: str
        sex: str
        face: str
        face_nft: bool
        sign: str
        rank: int = None
        level: int
        silence: bool
        fans_badge: bool
        fans_medal: FansMedal
        is_followed: bool
        top_photo: str  # 头图

    data: UserInfoResponseData = None


class UserBestVideoResponse(BaseResponse):
    class BestVideo(BaseModel):
        aid: int
        videos: int
        tid: int
        tname: str
        copyright: VideoCopyright
        pic: str
        title: str
        desc: str
        state: VideoState
        duration: timedelta
        owner: Owner
        dynamic: str
        stat: Stat
        cid: int
        bvid: str
        dimension: Dimension
        reason: str
        inter_video: bool

    data: List[BestVideo]


class UserVideoResponse(BaseResponse):
    class UserVideoResponseData(BaseModel):
        class RList(BaseModel):
            class Video(BaseModel):
                aid: int
                bvid: str
                author: str
                description: str
                length: str  # MM:SS
                mid: int
                title: str
                pic: str

            tlist: dict
            vlist: List[Video]

        class Page(BaseModel):
            count: int

        list: RList
        page: Page

    data: UserVideoResponseData = None


class AudioPlaylist(BaseModel):
    id: int = None  # 音频收藏夹mlid
    uid: int
    uname: str
    title: str
    type: int
    published: bool = None  # 是否公开
    cover: str
    song: int = None  # 音乐数量
    snum: int = None  # 音乐数量
    desc: str = None
    intro: str = None
    sids: List[int] = None  # 音频id列表
    menuId: int  # 对应歌单id
    statistic: dict


class AudioFavoriteListResponse(BaseResponse):
    class AudioFavoriteListResponseData(BaseModel):
        curPage: int
        pageCount: int
        totalSize: int
        pageSize: int
        data: List[AudioPlaylist]

    data: AudioFavoriteListResponseData = None


class AudioPlaylistSong(BaseModel):
    aid: int
    author: str
    bvid: str
    cid: int
    cover: str
    duration: timedelta
    id: int
    intro: str
    lyric: str
    title: str
    uid: int
    uname: str


class AudioFavoriteSongsResponse(BaseResponse):
    class AudioFavoriteSongsResponseData(BaseModel):
        curPage: int
        pageCount: int
        totalSize: int
        pageSize: int
        data: List[AudioPlaylistSong]

    data: AudioFavoriteSongsResponseData = None


class AudioFavoriteInfoResponse(BaseResponse):
    data: AudioPlaylist = None


class AudioGetUrlResponse(BaseResponse):
    class AudioGetUrlResponseData(BaseModel):
        cdns: List[str]
        sid: int
        size: int
        type: int

    data: AudioGetUrlResponseData = None


class VideoGetRelatedResponse(BaseResponse):
    class VideoGetRelatedResponseData(BaseModel):
        bvid: str
        aid: int
        videos: int  # 分P总数
        tid: int  # 分区id
        tname: str  # 子分区名称
        copyright: VideoCopyright
        pic: str  # 封面
        title: str  # 标题
        desc: str  # 简介
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

    data: List[VideoGetRelatedResponseData] = None


class VideoHotCommentsResponse(BaseResponse):
    class VideoHotCommentsResponseData(BaseModel):
        class Reply(BaseModel):
            class Member(BaseModel):
                mid: int
                uname: str
                avatar: str

            class Content(BaseModel):
                message: str
                plat: int
                device: str

            rpid: int
            like: int
            ctime: datetime
            member: Member
            content: Content

        page: dict
        replies: List[Reply]

    data: VideoHotCommentsResponseData = None


class LiveFeedListResponse(BaseResponse):
    class LiveFeedListResponseData(BaseModel):
        class LiveFeed(BaseModel):
            area_id: int
            cover: str
            face: str
            link: str
            online: int
            parent_area_id: int
            pic: str
            roomid: int
            title: str
            uid: int
            uname: str

        page: int
        pagesize: int
        results: int
        list: List[LiveFeed]

    data: LiveFeedListResponseData = None


class LivePlayUrlResponse(BaseResponse):
    class LivePlayUrlResponseData(BaseModel):
        class Qn(BaseModel):
            qn: int
            desc: str

        class Durl(BaseModel):
            url: str
            order: int

        current_quality: int
        accept_quality: List[int]
        current_qn: int
        quality_description: List[Qn]
        durl: List[Durl]

    data: LivePlayUrlResponseData = None


class MediaGetListResponse(BaseResponse):
    class MediaGetListResponseData(BaseModel):
        class Episode(BaseModel):
            aid: int
            bvid: str
            badge: str  # 标签
            cid: int
            cover: str
            title: str
            subtitle: str
            vid: str
            long_title: str
            duration: timedelta

            @classmethod
            @validator('duration')
            def convert_ms(cls, v):
                return v / 1000

        bkg_cover: str = None
        cover: str
        episodes: List[Episode]
        evaluate: str  # 简介
        media_id: int
        season_id: int
        seasons: list = None
        section: list = None
        share_sub_title: str  # 备注
        square_cover: str  # 方形封面
        title: str
        subtitle: str
        type: MediaType
        up_info: dict = None

    result: MediaGetListResponseData = None
    data: Any = None


class MediaFavlistResponse(BaseResponse):
    class MediaFavlistResponseData(BaseModel):
        class MediaInfo(BaseModel):
            media_id: int
            season_id: int
            season_type: int
            season_type_name: str
            title: str
            cover: str
            total_count: int  # 总集数 -1 未完结
            is_finish: bool  # 是否完结
            evaluate: str  # 简介
            subtitle: str

        pn: int
        ps: int
        total: int
        list: List[MediaInfo]

    data: MediaFavlistResponseData = None


class UserFollowingResponse(BaseResponse):
    class UserFollowingResponseData(BaseModel):
        class UserFollowing(BaseModel):
            mid: int
            uname: str
            face: str
            sign: str

        total: int
        list: List[UserFollowing]

    data: UserFollowingResponseData = None


class VideoMostPopularResponse(BaseResponse):
    class VideoMostPopularResponseData(BaseModel):
        class PopularVideo(BaseModel):
            aid: int
            bvid: str
            videos: int
            tid: int
            tname: str
            copyright: VideoCopyright
            pic: str
            title: str
            pubdate: datetime
            ctime: datetime
            desc: str
            duration: timedelta
            owner: Owner
            stat: Stat
            rcmd_reason: dict

        list: List[PopularVideo]

    data: VideoMostPopularResponseData = None


class VideoWeeklyListResponse(BaseResponse):
    class VideoWeeklyListResponseData(BaseModel):
        class VideoWeeklyItem(BaseModel):
            number: int
            subject: str
            status: int
            name: str

        list: List[VideoWeeklyItem]

    data: VideoWeeklyListResponseData = None
