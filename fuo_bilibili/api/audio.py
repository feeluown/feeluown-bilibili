from typing import Type, Any, Optional, Union

from pydantic import BaseModel

from fuo_bilibili.api.schema.requests import BaseRequest, PaginatedRequest, AudioFavoriteSongsRequest, \
    AudioGetUrlRequest
from fuo_bilibili.api.schema.responses import BaseResponse, AudioFavoriteListResponse, AudioFavoriteSongsResponse, \
    AudioFavoriteInfoResponse, AudioGetUrlResponse


class AudioMixin:
    API_AUDIO_BASE = 'https://www.bilibili.com/audio'

    def get(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def get_uncached(self, url: str, param: Optional[BaseRequest], clazz: Union[Type[BaseResponse], Type[BaseModel], None], **kwargs) -> Any:
        pass

    def audio_favorite_list(self, request: PaginatedRequest) -> AudioFavoriteListResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/collections/list'
        return self.get(url, request, AudioFavoriteListResponse)

    def audio_collected_list(self, request: PaginatedRequest) -> AudioFavoriteListResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/collect/menus'
        return self.get(url, request, AudioFavoriteListResponse)

    def audio_favorite_info(self, request: AudioFavoriteSongsRequest) -> AudioFavoriteInfoResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/collections/info'
        return self.get(url, request, AudioFavoriteInfoResponse)

    def audio_collected_info(self, request: AudioFavoriteSongsRequest) -> AudioFavoriteInfoResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/menu/info'
        return self.get(url, request, AudioFavoriteInfoResponse)

    def audio_favorite_songs(self, request: AudioFavoriteSongsRequest) -> AudioFavoriteSongsResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/song/of-coll'
        return self.get(url, request, AudioFavoriteSongsResponse)

    def audio_collected_songs(self, request: AudioFavoriteSongsRequest) -> AudioFavoriteSongsResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/song/of-menu'
        return self.get(url, request, AudioFavoriteSongsResponse)

    def audio_get_url(self, request: AudioGetUrlRequest) -> AudioGetUrlResponse:
        url = f'{self.API_AUDIO_BASE}/music-service-c/web/url'
        return self.get(url, request, AudioGetUrlResponse)
