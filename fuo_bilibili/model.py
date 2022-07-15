from typing import List

from bs4 import BeautifulSoup
from feeluown.library import SongModel, BriefArtistModel, PlaylistModel, BriefPlaylistModel, BriefUserModel, \
    BriefSongModel
from feeluown.models import SearchModel, ModelExistence

from fuo_bilibili import __identifier__
from fuo_bilibili.api import SearchType
from fuo_bilibili.api.schema.requests import SearchRequest
from fuo_bilibili.api.schema.responses import SearchResponse, SearchResultVideo, VideoInfoResponse, \
    FavoriteListResponse, FavoriteInfoResponse, FavoriteResourceResponse

PROVIDER_ID = __identifier__


class BSongModel(SongModel):
    source: str = PROVIDER_ID

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
    def create_brief_model(cls, fav: FavoriteListResponse.FavoriteListResponseData.FavoriteList):
        return BriefPlaylistModel(
            source=PROVIDER_ID,
            identifier=fav.id,
            creator_name='',
            name=fav.title,
        )

    @classmethod
    def create_info_model(cls, response: FavoriteInfoResponse):
        return cls(
            source=PROVIDER_ID,
            identifier=response.data.id,
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
    def create_model_list(cls, response: FavoriteListResponse):
        return [cls.create_brief_model(f) for f in response.data.list]
