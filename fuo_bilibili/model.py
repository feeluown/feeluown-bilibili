from typing import List, Union, Optional, Tuple

from bs4 import BeautifulSoup
from feeluown.library import SongModel, BriefArtistModel, PlaylistModel, BriefPlaylistModel, BriefUserModel, \
    BriefSongModel, ArtistModel, CommentModel, VideoModel, BriefVideoModel, BriefAlbumModel, AlbumModel
from feeluown.models import SearchModel, ModelExistence

from fuo_bilibili import __identifier__
from fuo_bilibili.api import SearchType
from fuo_bilibili.api.schema.requests import SearchRequest
from fuo_bilibili.api.schema.responses import SearchResponse, SearchResultVideo, VideoInfoResponse, \
    FavoriteListResponse, FavoriteInfoResponse, FavoriteResourceResponse, CollectedFavoriteListResponse, \
    FavoriteSeasonResourceResponse, HistoryLaterVideoResponse, HomeDynamicVideoResponse, UserInfoResponse, \
    UserBestVideoResponse, UserVideoResponse, AudioFavoriteSongsResponse, AudioFavoriteListResponse, AudioPlaylist, \
    AudioPlaylistSong, VideoHotCommentsResponse, SearchResultUser, LiveFeedListResponse, SearchResultLiveRoom, \
    SearchResultMedia, MediaGetListResponse, VideoWeeklyListResponse
from fuo_bilibili.util import format_timedelta_to_hms

PROVIDER_ID = __identifier__


class BBriefAlbumModel(BriefAlbumModel):
    cover: str = ''


class BSongModel(SongModel):
    source: str = PROVIDER_ID

    lyric: str = None

    @classmethod
    def create_audio_model(cls, au: AudioPlaylistSong) -> Optional['BSongModel']:
        return cls(
            source=__identifier__,
            identifier=f'audio_{au.id}',
            album=BBriefAlbumModel(
                source=PROVIDER_ID,
                identifier=au.uid,
                name=au.author,
                artists_name=au.author,
                cover=au.cover,
            ),
            title=au.title,
            artists=[BriefArtistModel(
                source=PROVIDER_ID,
                identifier=au.uid,
                name=au.author,
            )],
            duration=au.duration.total_seconds() * 1000,
            lyric=au.lyric,
        )

    @classmethod
    def create_user_brief_model(cls, media: UserVideoResponse.UserVideoResponseData.RList.Video):
        return BriefSongModel(
            source=__identifier__,
            identifier=media.bvid,
            title=media.title,
            artists_name=media.author,
            duration_ms=media.length
        )

    @classmethod
    def create_hot_model(cls, item: UserBestVideoResponse.BestVideo):
        return cls(
            source=__identifier__,
            identifier=item.bvid,
            album=BBriefAlbumModel(
                source=PROVIDER_ID,
                identifier=item.owner.mid,
                name=item.owner.name,
                artists_name=item.owner.name,
                cover=item.owner.face,
            ),
            title=BeautifulSoup(item.title).get_text(),
            artists=[BriefArtistModel(
                source=PROVIDER_ID,
                identifier=item.owner.mid,
                name=item.owner.name,
            )],
            duration=item.duration.total_seconds() * 1000,
        )

    @classmethod
    def create_dynamic_brief_model(cls, item: HomeDynamicVideoResponse.HomeDynamicVideoResponseData.DynamicVideoItem):
        media = item.modules.module_dynamic.major.archive
        author = item.modules.module_author
        return BriefSongModel(
            source=__identifier__,
            identifier=media.bvid,
            title=media.title,
            artists_name=author.name,
            duration_ms=media.duration_text,
        )

    @classmethod
    def create_brief_model(cls, media: FavoriteResourceResponse.FavoriteResourceResponseData.Media) -> BriefSongModel:
        return BriefSongModel(
            source=__identifier__,
            identifier=media.bvid,
            title=media.title,
            artists_name=media.upper.name,
            duration_ms=format_timedelta_to_hms(media.duration)
        )

    @classmethod
    def create_model(cls, result: SearchResultVideo) -> 'BSongModel':
        return cls(
            source=__identifier__,
            identifier=result.bvid,
            album=BBriefAlbumModel(
                source=PROVIDER_ID,
                identifier=result.mid,
                name=result.author,
                artists_name=result.author,
                cover=result.pic,
            ),
            title=BeautifulSoup(result.title).get_text(),
            artists=[BriefArtistModel(
                source=PROVIDER_ID,
                identifier=result.mid,
                name=result.author,
            )],
            duration=result.duration.total_seconds() * 1000,
        )

    @classmethod
    def create_info_model(cls, response: VideoInfoResponse) -> 'BSongModel':
        result = response.data
        lrc = None
        if result.subtitle.list is not None and len(result.subtitle.list) > 0:
            lrc = result.subtitle.list[0].subtitle_url
        return cls(
            source=__identifier__,
            identifier=result.bvid,
            album=BBriefAlbumModel(
                source=PROVIDER_ID,
                identifier=result.owner.mid,
                name=result.owner.name,
                artists_name=result.owner.name,
                cover=result.owner.face,
            ),
            title=result.title,
            artists=[BriefArtistModel(
                source=PROVIDER_ID,
                identifier=result.owner.mid,
                name=result.owner.name,
            )],
            duration=result.duration.total_seconds() * 1000,
            lyric=lrc,
            exists=ModelExistence.yes,
        )

    @classmethod
    def create_history_brief_model(cls, media):
        return BriefSongModel(
            source=__identifier__,
            identifier=media.bvid,
            title=media.title,
            artists_name=media.owner.name,
            duration_ms=format_timedelta_to_hms(media.duration)
        )

    @classmethod
    def create_history_brief_model_list(cls, resp: HistoryLaterVideoResponse) -> List[BriefSongModel]:
        if resp.data.list is None:
            return []
        return [cls.create_history_brief_model(media) for media in resp.data.list]


class BAlbumModel(AlbumModel):
    @staticmethod
    def create_episode_song_model(ep: MediaGetListResponse.MediaGetListResponseData.Episode,
                                  media: MediaGetListResponse.MediaGetListResponseData) -> BSongModel:
        return BSongModel(
            source=__identifier__,
            identifier=ep.bvid,
            album=BBriefAlbumModel(
                source=PROVIDER_ID,
                identifier=f'media_{media.media_id}_{media.season_id}',
                name=BeautifulSoup(media.title).text,
                artists_name='',
                cover=media.cover,
            ),
            title=ep.long_title,
            artists=[],
            duration=ep.duration.total_seconds(),
        )

    @classmethod
    def create_season_model(cls, media: MediaGetListResponse.MediaGetListResponseData) -> 'BAlbumModel':
        return cls(
            source=PROVIDER_ID,
            identifier=f'media_{media.media_id}_{media.season_id}',
            name=BeautifulSoup(media.title).text,
            artists=[],
            songs=[cls.create_episode_song_model(ep, media) for ep in media.episodes],
            cover=media.cover.replace('http://', 'https://'),
            description=media.evaluate,
        )


class BSearchModel(SearchModel):
    PROVIDER_ID = __identifier__

    # ['q', 'songs', 'playlists', 'artists', 'albums', 'videos']
    q: str
    songs = List[BSongModel]

    @staticmethod
    def search_user_model(user: SearchResultUser):
        return BriefArtistModel(
            source=PROVIDER_ID,
            identifier=user.mid,
            name=user.uname,
        )

    @staticmethod
    def search_media_model(media: SearchResultMedia):
        return BBriefAlbumModel(
            source=PROVIDER_ID,
            identifier=f'media_{media.media_id}_{media.season_id}',
            name=BeautifulSoup(media.title).text,
            artists_name='',
            cover=media.cover.replace('http://', 'https://'),
        )

    @staticmethod
    def search_live_model(live: SearchResultLiveRoom):
        return BVideoModel(
            source=PROVIDER_ID,
            identifier=f'live_{live.roomid}',
            title=live.title,
            artists=[
                BriefArtistModel(
                    source=PROVIDER_ID,
                    identifier=live.uid,
                    name=live.uname
                )
            ],
            duration=0,
            cover=f'https:{live.user_cover}',
        )

    @classmethod
    def create_model(cls, request: SearchRequest, response: Union[SearchResponse, Tuple[SearchResponse]]):
        songs = None
        artists = None
        videos = None
        albums = None
        if isinstance(response, Tuple):
            results = []
            for r in response:
                if r.data.result is None:
                    continue
                results += r.data.result
        else:
            results = response.data.result or []
        # fixme: implements multiple search types
        match SearchType.BANGUMI if isinstance(request, Tuple) else request.search_type:
            case SearchType.VIDEO:
                songs = list(map(lambda r_: BSongModel.create_model(r_), results))
            case SearchType.BILI_USER:
                artists = list(map(cls.search_user_model, results))
            case SearchType.LIVE_ROOM:
                videos = list(map(cls.search_live_model, results))
            case SearchType.BANGUMI:
                albums = list(map(cls.search_media_model, results))
        return cls(
            source=PROVIDER_ID,
            q=request[0].keyword if isinstance(request, Tuple) else request.keyword,
            songs=songs,
            artists=artists,
            videos=videos,
            albums=albums,
        )


class BPlaylistModel(PlaylistModel):
    PROVIDER_ID = __identifier__

    count: int

    @classmethod
    def create_audio_model(cls, p: AudioPlaylist):
        identifier = None
        desc = ''
        count = 0
        match p.type:
            case 1:
                identifier = f'audio_{p.type}_{p.id}'
                count = p.song or 0
                desc = p.desc
            case 2:
                identifier = f'audio_{p.type}_{p.menuId}'
                count = p.snum or 0
                desc = p.intro
        if identifier is None:
            return None
        return cls(
            source=PROVIDER_ID,
            identifier=identifier,
            creator=BriefUserModel(
                source=PROVIDER_ID,
                identifier=p.uid,
                name=p.uname
            ),
            name=f'{p.title} (音频)',
            cover='',
            description=desc,
            count=count,
        )

    @classmethod
    def create_audio_brief_model(cls, p: AudioPlaylist):
        identifier = None
        match p.type:
            case 1:
                identifier = f'audio_{p.type}_{p.id}'
            case 2:
                identifier = f'audio_{p.type}_{p.menuId}'
        if identifier is None:
            return None
        return BriefPlaylistModel(
            source=PROVIDER_ID,
            identifier=identifier,
            creator_name=p.uname,
            name=f'{p.title} (音频)',
        )

    @classmethod
    def weekly_brief_model(cls, item: VideoWeeklyListResponse.VideoWeeklyListResponseData.VideoWeeklyItem):
        return BriefPlaylistModel(
            source=PROVIDER_ID,
            identifier=f'weekly_{item.number}',
            creator_name='',
            name=f'{item.subject} ({item.name})',
        )

    @classmethod
    def create_audio_model_list(cls, resp: AudioFavoriteListResponse) -> List[BriefPlaylistModel]:
        return [cls.create_audio_brief_model(p) for p in resp.data.data]

    @classmethod
    def create_brief_model(cls, fav: Union[FavoriteListResponse.FavoriteListResponseData.FavoriteList,
                                           CollectedFavoriteListResponse.CollectedFavoriteListResponseData
                           .CollectedFavoriteList]):
        return BriefPlaylistModel(
            source=PROVIDER_ID,
            identifier=f'{fav.type}_{fav.id}',
            creator_name='',
            name=fav.title,
        )

    @classmethod
    def special_brief_playlists(cls):
        return [
            BriefPlaylistModel(
                source=PROVIDER_ID,
                identifier=f'DYNAMIC',
                creator_name='',
                name='动态视频',
            ),
            BriefPlaylistModel(
                source=PROVIDER_ID,
                identifier=f'LATER',
                creator_name='',
                name='稍后再看',
            ),
            BriefPlaylistModel(
                source=PROVIDER_ID,
                identifier=f'HISTORY',
                creator_name='',
                name='历史记录',
            ),
        ]

    @classmethod
    def special_model(cls, identifier, resp: Optional[HistoryLaterVideoResponse]):
        match identifier:
            case 'DYNAMIC':
                return cls(
                    source=PROVIDER_ID,
                    identifier=f'DYNAMIC',
                    creator=None,
                    name='动态视频',
                    cover='',
                    description='动态视频',
                    count=1000,
                )
            case 'LATER':
                return cls(
                    source=PROVIDER_ID,
                    identifier=f'LATER',
                    creator=None,
                    name='稍后再看',
                    cover='',
                    description='稍后再看',
                    count=resp.data.count if resp is not None else None,
                )
            case 'HISTORY':
                return cls(
                    source=PROVIDER_ID,
                    identifier=f'HISTORY',
                    creator=None,
                    name='历史纪录',
                    cover='',
                    description='历史纪录',
                    count=1000,
                )

    @classmethod
    def create_info_model(cls, response: Union[FavoriteInfoResponse, FavoriteSeasonResourceResponse]):
        if isinstance(response, FavoriteSeasonResourceResponse):
            return cls(
                source=PROVIDER_ID,
                identifier=f'21_{response.data.info.id}',
                creator=BriefUserModel(
                    source=PROVIDER_ID,
                    identifier=response.data.info.upper.mid,
                    name=response.data.info.upper.name,
                ),
                name=response.data.info.title,
                cover=response.data.info.cover,
                description=f'{response.data.info.media_count}个视频，{response.data.info.cnt_info.play}播放',
                count=response.data.info.media_count,
            )
        else:
            return cls(
                source=PROVIDER_ID,
                identifier=f'{response.data.type}_{response.data.id}',
                creator=BriefUserModel(
                    source=PROVIDER_ID,
                    identifier=response.data.upper.mid,
                    name=response.data.upper.name,
                ),
                name=response.data.title,
                cover=response.data.cover,
                description=response.data.intro,
                count=response.data.media_count,
            )

    @classmethod
    def create_model_list(cls, response: Union[FavoriteListResponse, CollectedFavoriteListResponse]):
        return [cls.create_brief_model(f) for f in response.data.list]


class BArtistModel(ArtistModel):
    PROVIDER_ID = __identifier__

    @classmethod
    def create_model(cls, resp: UserInfoResponse, video_resp: UserBestVideoResponse) -> 'BArtistModel':
        alias = []
        if resp.data.fans_badge and resp.data.fans_medal.show and resp.data.fans_medal.wear \
                and resp.data.fans_medal.medal is not None:
            alias.append(f'Lv{resp.data.fans_medal.medal.level} {resp.data.fans_medal.medal.medal_name}')
        return cls(
            source=PROVIDER_ID,
            identifier=resp.data.mid,
            name=resp.data.name,
            pic_url=resp.data.face,
            aliases=alias,
            hot_songs=[BSongModel.create_hot_model(v) for v in video_resp.data],
            description=resp.data.sign
        )


class BCommentModel(CommentModel):
    PROVIDER_ID = __identifier__

    @classmethod
    def create_model(cls, reply: VideoHotCommentsResponse.VideoHotCommentsResponseData.Reply):
        return cls(
            source=PROVIDER_ID,
            identifier=str(reply.rpid),
            user=BriefUserModel(
                source=PROVIDER_ID,
                identifier=reply.member.mid,
                name=reply.member.uname
            ),
            content=reply.content.message,
            liked_count=reply.like,
            time=int(reply.ctime.timestamp())
        )


class BVideoModel(VideoModel):
    @classmethod
    def create_live_model(cls, live: LiveFeedListResponse.LiveFeedListResponseData.LiveFeed):
        return cls(
            source=PROVIDER_ID,
            identifier=f'live_{live.roomid}',
            title=live.title,
            artists=[
                BriefArtistModel(
                    source=PROVIDER_ID,
                    identifier=live.uid,
                    name=live.uname
                )
            ],
            duration=0,
            cover=live.cover,
        )
