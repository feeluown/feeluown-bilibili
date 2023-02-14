import math
from inspect import signature
from pathlib import Path
from time import time
from typing import List, Optional, Union, Tuple

from feeluown.excs import NoUserLoggedIn
from feeluown.library import AbstractProvider, ProviderV2, ProviderFlags as Pf, UserModel, VideoModel, \
    BriefPlaylistModel, BriefSongModel, LyricModel, SupportsSongSimilar, BriefSongProtocol, SupportsSongHotComments, \
    SupportsAlbumGet, BriefAlbumModel, SupportsPlaylistAddSong, SupportsPlaylistRemoveSong, BriefUserModel, \
    BriefArtistModel
from feeluown.media import Quality, Media, MediaType, VideoAudioManifest
from feeluown.models import SearchType as FuoSearchType, ModelType
from feeluown.utils.reader import SequentialReader

from fuo_bilibili import __identifier__, __alias__
from fuo_bilibili.api import BilibiliApi, SearchRequest, SearchType as BilibiliSearchType, VideoInfoRequest, \
    PlayUrlRequest, VideoQualityNum
from fuo_bilibili.api.schema.enums import VideoFnval, CommentType
from fuo_bilibili.api.schema.requests import PasswordLoginRequest, SendSmsCodeRequest, SmsCodeLoginRequest, \
    FavoriteListRequest, FavoriteInfoRequest, FavoriteResourceRequest, CollectedFavoriteListRequest, \
    FavoriteSeasonResourceRequest, PaginatedRequest, HomeRecommendVideosRequest, HomeDynamicVideoRequest, \
    UserInfoRequest, UserBestVideoRequest, UserVideoRequest, AudioFavoriteSongsRequest, AudioGetUrlRequest, \
    VideoHotCommentsRequest, AnotherPaginatedRequest, LivePlayUrlRequest, MediaGetListRequest, MediaFavlistRequest, \
    HistoryAddLaterVideosRequest, HistoryDelLaterVideosRequest, FavoriteResourceOperateRequest, FavoriteNewRequest, \
    UserFollowingRequest
from fuo_bilibili.api.schema.responses import RequestCaptchaResponse, RequestLoginKeyResponse, PasswordLoginResponse, \
    SendSmsCodeResponse, SmsCodeLoginResponse, NavInfoResponse, PlayUrlResponse
from fuo_bilibili.const import DANMAKU_DIRECTORY
from fuo_bilibili.danmaku2ass import Danmaku2ASS
from fuo_bilibili.model import BSearchModel, BSongModel, BPlaylistModel, BArtistModel, BCommentModel, BVideoModel, \
    BAlbumModel
from fuo_bilibili.util import json_to_lrc_text

SEARCH_TYPE_MAP = {
    FuoSearchType.vi: BilibiliSearchType.LIVE_ROOM,  # 对应直播间
    FuoSearchType.ar: BilibiliSearchType.BILI_USER,  # 对应B站用户
    FuoSearchType.so: BilibiliSearchType.VIDEO,  # 对应投稿视频
    FuoSearchType.al: (BilibiliSearchType.MEDIA, BilibiliSearchType.BANGUMI),  # 对应番剧电影
}


class BilibiliProvider(AbstractProvider, ProviderV2, SupportsSongSimilar, SupportsSongHotComments, SupportsAlbumGet,
                       SupportsPlaylistAddSong, SupportsPlaylistRemoveSong):
    def playlist_add_song(self, playlist, song) -> bool:
        match playlist.identifier:
            case 'LATER':
                self._api.history_add_later_videos(HistoryAddLaterVideosRequest(bvid=song.identifier))
                return True
            case 'HISTORY':
                return False
        if playlist.identifier.startswith('audio_') or song.identifier.startswith('audio_'):
            return False
        _, id_ = playlist.identifier.split('_')
        self._api.favorite_resource_operate(FavoriteResourceOperateRequest(
            rid=self._get_video_avid(song.identifier),
            add_media_ids=str(id_)
        ))
        return True

    def playlist_remove_song(self, playlist, song) -> bool:
        match playlist.identifier:
            case 'LATER':
                self._api.history_del_later_videos(HistoryDelLaterVideosRequest(aid=self._get_video_avid(song.identifier)))
                return True
            case 'HISTORY':
                return False
        if playlist.identifier.startswith('audio_') or song.identifier.startswith('audio_'):
            return False
        self._api.favorite_resource_operate(FavoriteResourceOperateRequest(
            rid=self._get_video_avid(song.identifier),
            del_media_ids=str(playlist.identifier)
        ))
        return True

    # noinspection PyPep8Naming
    class meta:
        identifier: str = __identifier__
        name: str = __alias__
        flags: dict = {
            ModelType.song: (Pf.model_v2 | Pf.get | Pf.multi_quality | Pf.lyric | Pf.mv | Pf.similar | Pf.hot_comments),
            ModelType.video: (Pf.model_v2 | Pf.multi_quality | Pf.get),
            ModelType.playlist: (Pf.model_v2 | Pf.get | Pf.songs_rd | Pf.add_song | Pf.remove_song),
            ModelType.artist: (Pf.model_v2 | Pf.get | Pf.songs_rd),
            ModelType.album: (Pf.model_v2 | Pf.get),
        }

    def __init__(self):
        super(BilibiliProvider, self).__init__()
        self._api = BilibiliApi()
        self._user = None
        self._video_quality_codes = dict()
        self._video_cids = dict()
        self._video_avids = dict()

    def _format_search_request(self, keyword, type_) -> Union[SearchRequest, Tuple[SearchRequest]]:
        btype = SEARCH_TYPE_MAP.get(type_)
        if btype is None:
            raise NotImplementedError
        if isinstance(btype, Tuple):
            return tuple([SearchRequest(search_type=t, keyword=keyword) for t in btype])
        return SearchRequest(search_type=btype, keyword=keyword)

    def request_captcha(self) -> RequestCaptchaResponse.RequestCaptchaResponseData:
        res = self._api.request_captcha()
        assert hasattr(res.data, 'geetest') and res.data.geetest is not None
        return res.data

    def request_key(self) -> RequestLoginKeyResponse:
        return self._api.request_login_key()

    def cookie_check(self):
        return self._api.cookie_check()

    def auth(self, _):
        self._api.load_cookies()
        try:
            self._user = self.user_info()
        except RuntimeError as re:
            self._api.remove_cookie()
            print(str(re) + ' 请重新登录')
        return self._user

    def has_current_user(self) -> bool:
        return self._user is not None

    def get_current_user(self):
        if self._user is None:
            raise NoUserLoggedIn

    def user_info(self) -> UserModel:
        data: NavInfoResponse.NavInfoResponseData = self._api.nav_info().data
        user = UserModel(
            source=__identifier__,
            identifier=str(data.mid),
            name=data.uname,
            avatar_url=data.face
        )
        return user

    def sms_send_code(self, request: SendSmsCodeRequest) -> SendSmsCodeResponse:
        return self._api.send_sms_code(request)

    def password_login(self, request: PasswordLoginRequest) -> PasswordLoginResponse:
        return self._api.password_login(request)

    def sms_code_login(self, request: SmsCodeLoginRequest) -> SmsCodeLoginResponse:
        return self._api.sms_code_login(request)

    def search(self, keyword, type_, *args, **kwargs) -> Optional[BSearchModel]:
        request = self._format_search_request(keyword, type_)
        if isinstance(request, Tuple):
            response = tuple([self._api.search(r) for r in request])
        else:
            response = self._api.search(request)
        return BSearchModel.create_model(request, response)

    def song_get(self, identifier) -> Optional[BSongModel]:
        if identifier.startswith('audio_'):
            return None
        response = self._api.video_get_info(VideoInfoRequest(bvid=identifier))
        return BSongModel.create_info_model(response)

    def song_list_similar(self, song: BriefSongProtocol) -> List[BriefSongModel]:
        if song.identifier.startswith('audio_'):
            return []
        resp = self._api.video_get_related(VideoInfoRequest(bvid=song.identifier))
        return [BSongModel.create_history_brief_model(media) for media in resp.data]

    # noinspection PyProtocol
    def song_list_hot_comments(self, song: BriefSongProtocol) -> List[BCommentModel]:
        if song.identifier.startswith('audio_'):
            _, id_ = song.identifier.split('_')
            resp = self._api.video_get_hot_comments(VideoHotCommentsRequest(
                type=CommentType.audio, oid=int(id_), ps=10
            ))
        else:
            resp = self._api.video_get_hot_comments(VideoHotCommentsRequest(
                type=CommentType.video, oid=self._get_video_avid(song.identifier), ps=10
            ))
        return [BCommentModel.create_model(comment) for comment in resp.data.replies]

    def song_get_lyric(self, song) -> Optional[LyricModel]:
        if not hasattr(song, 'lyric') or song.lyric is None or len(song.lyric) == 0:
            song = self.song_get(song.identifier)
        if song.lyric is None:
            return None
        if song.lyric.endswith('.json'):
            json_data = self._api.get_content(song.lyric)
            return LyricModel(
                source=__identifier__,
                identifier=song.identifier,
                content=json_to_lrc_text(json_data),
            )
        else:
            return LyricModel(
                source=__identifier__,
                identifier=song.identifier,
                content=self._api.get_content(song.lyric),
            )

    def _get_video_avid(self, bvid: str) -> int:
        avid = self._video_avids.get(bvid)
        if avid is None:
            info = self._api.video_get_info(VideoInfoRequest(bvid=bvid))
            self._video_avids[bvid] = info.data.aid
            avid = info.data.aid
        return avid

    def _get_video_cid(self, bvid):
        cid = self._video_cids.get(bvid)
        if cid is None:
            info = self._api.video_get_info(VideoInfoRequest(bvid=bvid))
            self._video_cids[bvid] = info.data.cid
            cid = info.data.cid
        return cid

    def _get_video_dimension(self, bvid):
        info = self._api.video_get_info(VideoInfoRequest(bvid=bvid))
        return info.data.dimension.width, info.data.dimension.height

    def video_list_quality(self, video) -> List[Quality.Video]:
        if video.identifier.startswith('live_'):
            return [Quality.Video.hd]
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=video.identifier,
            cid=self._get_video_cid(video.identifier),
            fnval=VideoFnval.FLV
        ))
        qualities = set([q.get_quality() for q in response.data.accept_quality])
        self._video_quality_codes[video.identifier] = response.data.accept_quality
        return list(qualities)

    def song_get_mv(self, song) -> Optional[VideoModel]:
        if song.identifier.startswith('audio_'):
            return None
        song = self.song_get(song.identifier)
        return VideoModel(
            source=__identifier__,
            identifier=song.identifier,
            title=song.title,
            artists=song.artists,
            duration=song.duration,
            cover=''
        )

    def _get_video_danmaku(self, cid, bvid) -> Optional[Path]:
        # find existed ass file
        for p in DANMAKU_DIRECTORY.glob(f'{cid}.ass'):
            if p.is_file() and time() - p.stat().st_mtime < 300:
                return p
        # find existed xml file
        for p in DANMAKU_DIRECTORY.glob(f'{cid}.xml'):
            if p.is_file() and time() - p.stat().st_mtime < 300:
                width, height = self._get_video_dimension(bvid)
                target_file = p.with_suffix('.ass')
                font_size = 50 / 1080 * height
                Danmaku2ASS(p.as_posix(), 'autodetect', target_file.as_posix(), width, height, font_size=font_size)
                return target_file
        # get latest danmuku and transform to ass
        data = self._api.get_content_raw(f'https://comment.bilibili.com/{cid}.xml')
        xml_file = DANMAKU_DIRECTORY / f'{cid}.xml'
        xml_file.unlink(missing_ok=True)
        with xml_file.open('wb') as f:
            f.write(data)
            f.flush()
        target_file = xml_file.with_suffix('.ass')
        width, height = self._get_video_dimension(bvid)
        font_size = 50 / 1080 * height
        Danmaku2ASS(xml_file.as_posix(), 'autodetect', target_file.as_posix(), width, height, font_size=font_size)
        return target_file

    def video_get_media(self, video, quality: Quality.Video) -> Optional[Media]:
        if video.identifier.startswith('live_'):
            _, id_ = video.identifier.split('_')
            resp = self._api.live_play_url(LivePlayUrlRequest(cid=int(id_)))
            if resp.data.durl is None or len(resp.data.durl) == 0:
                return None
            return Media(resp.data.durl[0].url, format='m3u8',
                         http_headers={'Referer': 'https://www.bilibili.com/'})
        video_cid = self._get_video_cid(video.identifier)
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=video.identifier,
            qn=VideoQualityNum.q1080p60,
            cid=video_cid,
            fnval=VideoFnval.DASH
        ))
        # select audio
        audios = sorted(response.data.dash.audio, key=lambda a: a.bandwidth, reverse=True)
        if audios is None or len(audios) == 0:
            return None
        # select video
        print(response.data.dash.video)
        max_quality_code = VideoQualityNum.get_max_from_quality(quality)
        select_quality = max(filter(lambda c: c.value <= max_quality_code, self._video_quality_codes[video.identifier]),
                             key=lambda c: c.value)
        videos = sorted(filter(lambda a: a.id <= select_quality.value, response.data.dash.video), key=lambda a: a.id, reverse=True)
        if videos is None or len(videos) == 0:
            return None
        if len(signature(VideoAudioManifest).parameters) == 3:
            danmaku_path = self._get_video_danmaku(video_cid, video.identifier)
            if not danmaku_path.exists():
                danmaku_path = None
            manifest = VideoAudioManifest(videos[0].base_url, audios[0].base_url, danmaku_path.as_posix() if danmaku_path is not None else None)
        else:
            manifest = VideoAudioManifest(videos[0].base_url, audios[0].base_url)
        return Media(manifest, format='flv', http_headers={'Referer': 'https://www.bilibili.com/'})

    def song_list_quality(self, song) -> List[Quality.Audio]:
        if song.identifier.startswith('audio_'):
            return [Quality.Audio.hq]
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=song.identifier,
            cid=self._get_video_cid(song.identifier),
            fnval=VideoFnval.DASH
        ))
        song_bitrates = [a.bandwidth for a in response.data.dash.audio]
        qualities = []
        for b in song_bitrates:
            if b <= 120000:
                qualities.append(Quality.Audio.lq)
                continue
            if b <= 256000:
                qualities.append(Quality.Audio.sq)
                continue
            qualities.append(Quality.Audio.hq)
        print(list(set(qualities)))
        return list(set(qualities))

    def song_get_media(self, song, quality: Quality.Audio) -> Optional[Media]:
        if song.identifier.startswith('audio_'):
            _, id_ = song.identifier.split('_')
            resp = self._api.audio_get_url(AudioGetUrlRequest(sid=int(id_)))
            if len(resp.data.cdns) < 1:
                return None
            return Media(resp.data.cdns[0], type_=MediaType.audio, format='m4a',
                         http_headers={'Referer': 'https://www.bilibili.com/'})
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=song.identifier,
            cid=self._get_video_cid(song.identifier),
            fnval=VideoFnval.DASH
        ))
        audios = sorted(response.data.dash.audio, key=lambda a: a.bandwidth, reverse=True)
        selects: Optional[List[PlayUrlResponse.PlayUrlResponseData.Dash.DashItem]] = None
        match quality:
            case Quality.Audio.lq:
                selects = list(filter(lambda a: a.bandwidth <= 120000, audios))
            case Quality.Audio.sq:
                selects = list(filter(lambda a: a.bandwidth <= 256000, audios))
            case Quality.Audio.hq:
                selects = audios
        if selects is None or len(selects) == 0:
            return None
        return Media(selects[0].base_url, type_=MediaType.audio, format='m4s', bitrate=int(selects[0].bandwidth / 1000),
                     http_headers={'Referer': 'https://www.bilibili.com/'})

    def user_playlists(self, identifier) -> List[BriefPlaylistModel]:
        resp = self._api.favorite_list(FavoriteListRequest(up_mid=int(identifier)))
        return BPlaylistModel.create_model_list(resp)

    def user_playlist_new(self, title: str, intro: str, privacy: int = None):
        return self._api.favorite_new(FavoriteNewRequest(title=title, intro=intro, privacy=privacy))

    def fav_playlists(self, identifier) -> List[BriefPlaylistModel]:
        resp = self._api.collected_favorite_list(CollectedFavoriteListRequest(up_mid=int(identifier), ps=40))
        return BPlaylistModel.create_model_list(resp)

    def user_following(self) -> List[BriefArtistModel]:
        resp = self._api.user_following(UserFollowingRequest(vmid=int(self._user.identifier), ps=100))
        return [BriefArtistModel(
            source=__identifier__,
            identifier=user.mid,
            name=user.uname,
        ) for user in resp.data.list]

    def audio_favorite_playlists(self) -> List[BriefPlaylistModel]:
        resp = self._api.audio_favorite_list(PaginatedRequest(ps=100, pn=1))
        return BPlaylistModel.create_audio_model_list(resp)

    def audio_collected_playlists(self) -> List[BriefPlaylistModel]:
        resp = self._api.audio_collected_list(PaginatedRequest(ps=100, pn=1))
        return BPlaylistModel.create_audio_model_list(resp)

    def home_recommend_videos(self, idx) -> List[BriefSongModel]:
        resp = self._api.home_recommend_videos(HomeRecommendVideosRequest(ps=10, fresh_idx=idx, fresh_idx_1h=idx))
        return [BSongModel.create_history_brief_model(v) for v in resp.data.item]

    def most_popular_videos(self) -> List[BriefSongModel]:
        resp = self._api.video_most_popular()
        return [BSongModel.create_history_brief_model(v) for v in resp.data.list]

    def weekly_video_playlists(self) -> List[BriefPlaylistModel]:
        resp = self._api.video_weekly_list()
        return [BPlaylistModel.weekly_brief_model(v) for v in resp.data.list]

    def video_live_feeds(self) -> List[BVideoModel]:
        resp = self._api.live_feed_list(AnotherPaginatedRequest(pagesize=30))
        return [BVideoModel.create_live_model(live) for live in resp.data.list]

    def media_user_collect(self) -> List[BriefAlbumModel]:
        resp1 = self._api.media_bangumi_favlist(MediaFavlistRequest(vmid=int(self._user.identifier), ps=30))
        resp2 = self._api.media_bangumi_favlist(MediaFavlistRequest(vmid=int(self._user.identifier), ps=30, type=2))
        return [BSearchModel.search_media_model(m) for m in resp1.data.list] +\
               [BSearchModel.search_media_model(m) for m in resp2.data.list]

    def audio_playlist_get(self, identifier: str) -> Optional[BPlaylistModel]:
        _, type_, id_ = identifier.split('_')
        match int(type_):
            case 1:
                resp = self._api.audio_favorite_info(AudioFavoriteSongsRequest(sid=int(id_)))
                return BPlaylistModel.create_audio_model(resp.data)
            case 2:
                resp = self._api.audio_collected_info(AudioFavoriteSongsRequest(sid=int(id_)))
                return BPlaylistModel.create_audio_model(resp.data)
        return None

    def album_get(self, identifier: str) -> Optional[BAlbumModel]:
        if identifier.startswith('media_'):
            _, __, ssid = identifier.split('_')
            resp = self._api.media_bangumi_get_list(MediaGetListRequest(season_id=ssid))
            return BAlbumModel.create_season_model(resp.result)
        return None

    def playlist_get(self, identifier: str) -> Optional[BPlaylistModel]:
        # fixme: fuo should support playlist_get v2 first
        if identifier.startswith('weekly_'):
            return BPlaylistModel(
                source=__identifier__,
                identifier=identifier,
                creator=None,
                name='',
                cover='',
                description='',
                count=0,
            )
        if identifier.startswith('audio_'):
            return self.audio_playlist_get(identifier)
        if identifier == 'LATER':
            resp = self._api.history_later_videos()
            return BPlaylistModel.special_model(identifier, resp)
        if identifier in ['HISTORY', 'DYNAMIC']:
            return BPlaylistModel.special_model(identifier, None)
        fav_type, id_ = identifier.split('_')
        if int(fav_type) == 21:
            resp = self._api.favorite_season_resource(FavoriteSeasonResourceRequest(season_id=int(id_), ps=0))
        else:
            resp = self._api.favorite_info(FavoriteInfoRequest(media_id=int(id_)))
        return BPlaylistModel.create_info_model(resp)

    def audio_playlist_create_songs_rd(self, playlist):
        _, type_, id_ = playlist.identifier.split('_')

        if int(type_) == 2 and playlist.count == 0:
            # 兼容歌单信息不存在歌曲数量的问题
            response = self._api.audio_collected_songs(AudioFavoriteSongsRequest(
                sid=int(id_), pn=1, ps=0
            ))
            playlist.count = response.data.totalSize

        def g():
            page = 1
            while page <= math.ceil(playlist.count / 20):
                match int(type_):
                    case 1:
                        response = self._api.audio_favorite_songs(AudioFavoriteSongsRequest(
                            sid=int(id_), pn=page
                        ))
                        for au in response.data.data:
                            yield BSongModel.create_audio_model(au)
                    case 2:
                        response = self._api.audio_collected_songs(AudioFavoriteSongsRequest(
                            sid=int(id_), pn=page
                        ))
                        for au in response.data.data:
                            yield BSongModel.create_audio_model(au)
                page += 1

        return SequentialReader(g(), playlist.count)

    def playlist_create_songs_rd(self, playlist):
        if playlist.identifier.startswith('audio_'):
            return self.audio_playlist_create_songs_rd(playlist)

        def g():
            _dynamic_offset = None

            if playlist.identifier == 'LATER':
                response = self._api.history_later_videos()
                song_list = BSongModel.create_history_brief_model_list(response)
                for s in song_list:
                    yield s
            else:
                is_season = False
                id_ = None
                if playlist.identifier not in ['HISTORY', 'DYNAMIC']:
                    fav_type, id_ = playlist.identifier.split('_')
                    is_season = int(fav_type) == 21
                page = 1
                while page <= math.ceil(playlist.count / 20):
                    if playlist.identifier == 'DYNAMIC':
                        resp = self._api.home_dynamic_videos(HomeDynamicVideoRequest(offset=_dynamic_offset, page=page))
                        _dynamic_offset = resp.data.offset
                        for v in resp.data.items:
                            yield BSongModel.create_dynamic_brief_model(v)
                        if not resp.data.has_more:
                            return
                    elif playlist.identifier == 'HISTORY':
                        response = self._api.history_videos(PaginatedRequest(pn=page))
                        for m in response.data:
                            yield BSongModel.create_history_brief_model(m)
                    else:
                        if is_season:
                            response = self._api.favorite_season_resource(FavoriteSeasonResourceRequest(
                                season_id=int(id_),
                                pn=page,
                            ))
                        else:
                            response = self._api.favorite_resource(FavoriteResourceRequest(
                                media_id=int(id_),
                                pn=page,
                            ))
                        for m in response.data.medias:
                            yield BSongModel.create_brief_model(m)
                    page += 1

        return SequentialReader(g(), playlist.count)

    @staticmethod
    def special_playlists() -> List[BriefPlaylistModel]:
        return BPlaylistModel.special_brief_playlists()

    def artist_get(self, identifier) -> BArtistModel:
        resp = self._api.user_info(UserInfoRequest(mid=identifier))
        video_resp = self._api.user_best_videos(UserBestVideoRequest(vmid=identifier))
        return BArtistModel.create_model(resp, video_resp)

    def artist_create_songs_rd(self, artist):
        resp = self._api.user_videos(UserVideoRequest(mid=artist.identifier, ps=1, pn=1))
        total = resp.data.page.count

        def g():
            page = 1
            while page <= math.ceil(total / 20):
                response = self._api.user_videos(UserVideoRequest(mid=artist.identifier, ps=20, pn=page))
                for m in response.data.list.vlist:
                    yield BSongModel.create_user_brief_model(m)
                page += 1

        return SequentialReader(g(), total)

    @property
    def identifier(self):
        return __identifier__

    @property
    def name(self):
        return __alias__

    def close(self):
        self._api.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    from inspect import signature
    print(len(signature(VideoAudioManifest).parameters))
