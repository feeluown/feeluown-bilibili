import logging

from feeluown.gui.base_renderer import LibraryTabRendererMixin
from feeluown.gui.page_containers.table import Renderer
from feeluown.gui.widgets import TextButton
from feeluown.gui.widgets.tabbar import Tab

from fuo_bilibili import BilibiliProvider

logger = logging.getLogger(__name__)


async def render(req, **kwargs):
    app = req.ctx['app']
    app.ui.right_panel.set_body(app.ui.table_container)
    provider = app.library.get('bilibili')
    tab_id = Tab(int(req.query.get('tab_id', Tab.songs.value)))
    renderer = HomeRenderer(tab_id, provider)
    await app.ui.table_container.set_renderer(renderer)


class HomeRenderer(Renderer, LibraryTabRendererMixin):
    def __init__(self, tab_id, provider):
        self.refresh_btn = None
        self.tab_id = tab_id
        self._provider: BilibiliProvider = provider
        self._rcmd_index = 0

    async def render(self):
        self.render_tabbar()
        self.meta_widget.show()
        self.meta_widget.title = '我的主页'

        if self.tab_id == Tab.songs:
            self._refresh_home_videos()
            refresh_btn = TextButton('刷新', self.toolbar)
            # noinspection PyUnresolvedReferences
            refresh_btn.clicked.connect(self._refresh_home_videos)
            self.toolbar.add_tmp_button(refresh_btn)
        elif self.tab_id == Tab.videos:
            self._load_live_streams()
        elif self.tab_id == Tab.albums:
            self._load_bangumis()
        elif self.tab_id == Tab.artists:
            self._load_recent_following()

    def _load_recent_following(self):
        self.show_artists(self._provider.user_following())

    def _load_bangumis(self):
        self.show_albums(self._provider.media_user_collect())

    def _load_live_streams(self):
        self.show_videos(self._provider.video_live_feeds())

    def _refresh_home_videos(self):
        self._rcmd_index += 1
        self.show_songs(self._provider.home_recommend_videos(self._rcmd_index))

    def show_by_tab_id(self, tab_id):
        query = {'tab_id': tab_id.value}
        self._app.browser.goto(page='/providers/bilibili/home', query=query)

    def render_tabbar(self):
        super().render_tabbar()
        try:
            self.tabbar.songs_btn.setText('首页推荐')
            self.tabbar.albums_btn.setText('我的番剧/电影')
            self.tabbar.artists_btn.setText('最近关注')
            self.tabbar.videos_btn.setText('订阅直播')
            self.tabbar.playlists_btn.hide()
        except Exception as e:
            logger.warning(str(e))
