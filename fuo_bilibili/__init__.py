from typing import Optional, Union

from feeluown.app import App

__alias__ = '哔哩哔哩'
__feeluown_version__ = '3.5'
__version__ = '0.0.1'
__desc__ = __alias__
__identifier__ = 'bilibili'

from feeluown.app.gui_app import GuiApp

from fuo_bilibili.provider import BilibiliProvider
from fuo_bilibili.ui import BUiManager

provider = BilibiliProvider()
ui_mgr: Optional[BUiManager] = None


# noinspection PyProtectedMember
def enable(app: Union[App, GuiApp]):
    global ui_mgr
    app.library.register(provider)
    if app.mode & App.GuiMode:
        ui_mgr = BUiManager(app, provider)


def disable(app: App):
    app.library.deregister(provider)
    if app.mode & App.GuiMode:
        provider.close()
        # noinspection PyUnresolvedReferences
        app.providers.remove(provider.identifier)
