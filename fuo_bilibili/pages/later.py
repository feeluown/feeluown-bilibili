from feeluown.gui.base_renderer import LibraryTabRendererMixin
from feeluown.gui.page_containers.table import Renderer
from feeluown.gui.widgets.tabbar import Tab
from feeluown.utils import aio

from fuo_bilibili import BilibiliProvider


async def render(req, **kwargs):
    app = req.ctx['app']
    app.ui.right_panel.set_body(app.ui.table_container)
    provider: BilibiliProvider = app.library.get('bilibili')
    tab_id = Tab(int(req.query.get('tab_id', Tab.songs.value)))
    print(provider)
    # noinspection PyProtectedMember
    renderer = LaterRenderer(tab_id, provider)
    await app.ui.table_container.set_renderer(renderer)


class LaterRenderer(Renderer, LibraryTabRendererMixin):
    def show_by_tab_id(self, tab_id):
        query = {'tab_id': tab_id.value}
        self._app.browser.goto(page='/providers/bilibili/later', query=query)

    def __init__(self, tab_id, provider):
        self.tab_id = tab_id
        self._provider: BilibiliProvider = provider

    async def render(self):
        self.render_tabbar()
        self.meta_widget.show()
        self.meta_widget.title = '历史观看'

        if self.tab_id == Tab.songs:
            # 稍后再看
            self.show_songs(await aio.run_fn(self._provider.history_later_videos))

    def render_tabbar(self):
        super().render_tabbar()
        try:
            self.tabbar.songs_btn.setText('稍后再看')
            self.tabbar.albums_btn.hide()
            self.tabbar.artists_btn.hide()
            self.tabbar.videos_btn.hide()
            self.tabbar.playlists_btn.hide()
        except Exception:
            pass
