from feeluown.app import App

__alias__ = '哔哩哔哩'
__feeluown_version__ = '3.5'
__version__ = '0.0.1'
__desc__ = __alias__
__identifier__ = 'bilibili'

from fuo_bilibili.provider import BilibiliProvider

provider = BilibiliProvider()


# noinspection PyProtectedMember
def enable(app: App):
    app.library.register(provider)


def disable(app: App):
    app.library.deregister(provider)
