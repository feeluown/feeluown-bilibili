from typing import List, Union, Optional

from bs4 import BeautifulSoup
from feeluown.library import SongModel, BriefArtistModel, PlaylistModel, BriefPlaylistModel, BriefUserModel, \
    BriefSongModel, ArtistModel
from feeluown.models import SearchModel, ModelExistence

from fuo_bilibili import __identifier__
from fuo_bilibili.api import SearchType
from fuo_bilibili.api.schema.requests import SearchRequest
from fuo_bilibili.api.schema.responses import SearchResponse, SearchResultVideo, VideoInfoResponse, \
    FavoriteListResponse, FavoriteInfoResponse, FavoriteResourceResponse, CollectedFavoriteListResponse, \
    FavoriteSeasonResourceResponse, HistoryLaterVideoResponse, HomeDynamicVideoResponse, UserInfoResponse, \
    UserBestVideoResponse, UserVideoResponse

PROVIDER_ID = __identifier__


class BSongModel(SongModel):
    source: str = PROVIDER_ID

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
            album=None,
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
            duration_ms=str(media.duration).lstrip('0:')
        )

    @classmethod
    def create_model(cls, result: SearchResultVideo) -> 'BSongModel':
        return cls(
            source=__identifier__,
            identifier=result.bvid,
            album=None,
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
        return cls(
            source=__identifier__,
            identifier=result.bvid,
            album=None,
            title=result.title,
            artists=[BriefArtistModel(
                source=PROVIDER_ID,
                identifier=result.owner.mid,
                name=result.owner.name,
            )],
            duration=result.duration.total_seconds() * 1000,
            exists=ModelExistence.yes
        )

    @classmethod
    def create_history_brief_model(cls, media):
        return BriefSongModel(
            source=__identifier__,
            identifier=media.bvid,
            title=media.title,
            artists_name=media.owner.name,
            duration_ms=str(media.duration).lstrip('0:')
        )

    @classmethod
    def create_history_brief_model_list(cls, resp: HistoryLaterVideoResponse) -> List[BriefSongModel]:
        return [cls.create_history_brief_model(media) for media in resp.data.list]


class BSearchModel(SearchModel):
    PROVIDER_ID = __identifier__

    # ['q', 'songs', 'playlists', 'artists', 'albums', 'videos']
    q: str
    songs = List[BSongModel]

    @classmethod
    def create_model(cls, request: SearchRequest, response: SearchResponse):
        songs = None
        match request.search_type:
            case SearchType.VIDEO:
                songs = list(map(lambda r: BSongModel.create_model(r), response.data.result))
        return cls(
            source=PROVIDER_ID,
            q=request.keyword,
            songs=songs
        )


class BPlaylistModel(PlaylistModel):
    PROVIDER_ID = __identifier__

    count: int

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
