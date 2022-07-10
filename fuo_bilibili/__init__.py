from feeluown.app import App

# noinspection PyUnresolvedReferences,PyProtectedMember
from mpv import _mpv_set_option_string

__alias__ = '哔哩哔哩'
__feeluown_version__ = '3.5'
__version__ = '0.0.1'
__desc__ = __alias__
__identifier__ = 'bilibili'

from fuo_bilibili.provider import BilibiliProvider

provider = BilibiliProvider()


def enable(app: App):
    # noinspection PyProtectedMember
    _mpv_set_option_string(app.player._mpv.handle, b'http-header-fields',
                           b'Referer: https://www.bilibili.com, Origin: https://www.bilibili.com, '
                           b'Host: www.bilibili.com')
    app.library.register(provider)


def disable(app: App):
    app.library.deregister(provider)
