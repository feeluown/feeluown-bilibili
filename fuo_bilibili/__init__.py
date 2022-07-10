from feeluown.app import App

# noinspection PyUnresolvedReferences,PyProtectedMember,PyPackageRequirements
from mpv import _mpv_set_option_string, _mpv_set_property_string

__alias__ = '哔哩哔哩'
__feeluown_version__ = '3.5'
__version__ = '0.0.1'
__desc__ = __alias__
__identifier__ = 'bilibili'

from fuo_bilibili.provider import BilibiliProvider

provider = BilibiliProvider()


# noinspection PyProtectedMember
def enable(app: App):
    _mpv_set_option_string(app.player._mpv.handle, b'http-header-fields',
                           b'Referer: https://www.bilibili.com')
    _mpv_set_property_string(app.player._mpv.handle, b'http-header-fields',
                             b'Referer: https://www.bilibili.com')
    app.library.register(provider)


def disable(app: App):
    app.library.deregister(provider)
