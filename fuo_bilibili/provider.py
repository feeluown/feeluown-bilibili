import math
from typing import List, Optional

from feeluown.excs import NoUserLoggedIn
from feeluown.library import AbstractProvider, ProviderV2, ProviderFlags as Pf, UserModel, VideoModel, \
    BriefPlaylistModel, BriefSongModel
from feeluown.media import Quality, Media, MediaType
from feeluown.models import SearchType as FuoSearchType, ModelType
from feeluown.utils.reader import SequentialReader

from fuo_bilibili import __identifier__, __alias__
from fuo_bilibili.api import BilibiliApi, SearchRequest, SearchType as BilibiliSearchType, VideoInfoRequest, \
    PlayUrlRequest, VideoQualityNum
from fuo_bilibili.api.schema.enums import VideoFnval
from fuo_bilibili.api.schema.requests import PasswordLoginRequest, SendSmsCodeRequest, SmsCodeLoginRequest, \
    FavoriteListRequest, FavoriteInfoRequest, FavoriteResourceRequest, CollectedFavoriteListRequest, \
    FavoriteSeasonResourceRequest, PaginatedRequest, HomeRecommendVideosRequest, HomeDynamicVideoRequest, \
    UserInfoRequest, UserBestVideoRequest, UserVideoRequest
from fuo_bilibili.api.schema.responses import RequestCaptchaResponse, RequestLoginKeyResponse, PasswordLoginResponse, \
    SendSmsCodeResponse, SmsCodeLoginResponse, NavInfoResponse
from fuo_bilibili.model import BSearchModel, BSongModel, BPlaylistModel, BArtistModel

SEARCH_TYPE_MAP = {
    FuoSearchType.vi: BilibiliSearchType.VIDEO,
    FuoSearchType.ar: BilibiliSearchType.BILI_USER,
    FuoSearchType.so: BilibiliSearchType.VIDEO,
}


class BilibiliProvider(AbstractProvider, ProviderV2):
    # noinspection PyPep8Naming
    class meta:
        identifier: str = __identifier__
        name: str = __alias__
        flags: dict = {
            ModelType.song: (Pf.model_v2 | Pf.get | Pf.multi_quality | Pf.lyric | Pf.mv),
            ModelType.video: (Pf.model_v2 | Pf.multi_quality | Pf.get),
            ModelType.playlist: (Pf.model_v2 | Pf.get | Pf.songs_rd),
            ModelType.artist: (Pf.model_v2 | Pf.get | Pf.songs_rd),
        }

    def __init__(self):
        super(BilibiliProvider, self).__init__()
        self._api = BilibiliApi()
        self._user = None

    def _format_search_request(self, keyword, type_) -> SearchRequest:
        btype = SEARCH_TYPE_MAP.get(type_)
        if btype is None:
            raise NotImplementedError
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
        self._user = self.user_info()
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
        response = self._api.search(request)
        return BSearchModel.create_model(request, response)

    def song_get(self, identifier) -> BSongModel:
        response = self._api.video_get_info(VideoInfoRequest(bvid=identifier))
        return BSongModel.create_info_model(response)

    def song_get_lyric(self, song) -> None:
        return None

    def video_list_quality(self, video) -> List[Quality.Video]:
        return [Quality.Video.hd]

    def song_get_mv(self, song) -> Optional[VideoModel]:
        song = self.song_get(song.identifier)
        return VideoModel(
            source=__identifier__,
            identifier=song.identifier,
            title=song.title,
            artists=song.artists,
            duration=song.duration,
            cover=''
        )

    def video_get_media(self, video, quality) -> Optional[Media]:
        info = self._api.video_get_info(VideoInfoRequest(bvid=video.identifier))
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=video.identifier,
            qn=VideoQualityNum.q8k,
            cid=info.data.cid,
            fnval=VideoFnval.FLV
        ))
        return Media(response.data.durl[0].url, format='flv',
                     http_headers={'Referer': 'https://www.bilibili.com/'})

    def song_list_quality(self, song) -> List[Quality.Audio]:
        return [Quality.Audio.lq]

    def song_get_media(self, song, quality) -> Optional[Media]:
        info = self._api.video_get_info(VideoInfoRequest(bvid=song.identifier))
        response = self._api.video_get_url(PlayUrlRequest(
            bvid=song.identifier,
            qn=VideoQualityNum.q8k,
            cid=info.data.cid,
            fnval=VideoFnval.DASH
        ))
        return Media(response.data.dash.audio[0].base_url, type_=MediaType.audio, format='m4s', bitrate=320,
                     http_headers={'Referer': 'https://www.bilibili.com/'})

    def user_playlists(self, identifier) -> List[BriefPlaylistModel]:
        resp = self._api.favorite_list(FavoriteListRequest(up_mid=int(identifier)))
        return BPlaylistModel.create_model_list(resp)

    def fav_playlists(self, identifier) -> List[BriefPlaylistModel]:
        resp = self._api.collected_favorite_list(CollectedFavoriteListRequest(up_mid=int(identifier), ps=40))
        return BPlaylistModel.create_model_list(resp)

    def home_recommend_videos(self, idx) -> List[BriefSongModel]:
        resp = self._api.home_recommend_videos(HomeRecommendVideosRequest(ps=10, fresh_idx=idx, fresh_idx_1h=idx))
        return [BSongModel.create_history_brief_model(v) for v in resp.data.item]

    def playlist_get(self, identifier: str) -> BPlaylistModel:
        # fixme: fuo should support playlist_get v2 first
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

    def playlist_create_songs_rd(self, playlist):
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
