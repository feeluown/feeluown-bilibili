import asyncio
import logging
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QPushButton, QLabel, QFrame, QTabWidget, QMessageBox, \
    QAction, QInputDialog
from feeluown.app.gui_app import GuiApp
from feeluown.gui import ProviderUiManager
from feeluown.library import UserModel

from fuo_bilibili import __identifier__, __alias__, BilibiliProvider
from fuo_bilibili.api.schema.requests import PasswordLoginRequest, SendSmsCodeRequest, SmsCodeLoginRequest
from fuo_bilibili.api.schema.responses import RequestLoginKeyResponse
from fuo_bilibili.util import rsa_encrypt

logger = logging.getLogger(__name__)


class BAuthDialog(QDialog):
    """
    人机验证
    """
    # signal: validate, seccode, challenge, token, type
    auth_success = pyqtSignal(str, str, str, str, str)

    def __init__(self, parent=None, provider: BilibiliProvider = None):
        super(BAuthDialog, self).__init__(parent)
        self._token = None
        self.type = None
        self._provider = provider
        self.gt_input = QLineEdit(self)
        self.challenge_input = QLineEdit(self)
        self.gt_input.setReadOnly(True)
        self.gt_input.setVisible(False)
        self.challenge_input.setReadOnly(True)
        self.challenge_input.setVisible(False)
        self.auth_link = self._create_link_label('#', '正在获取验证链接...')
        self.validate_input = QLineEdit(self)
        self.validate_input.setPlaceholderText('validate')
        self.seccode_input = QLineEdit(self)
        self.seccode_input.setPlaceholderText('seccode')
        self.hint_label = QLabel(self)
        self.hint_label.setStyleSheet('QLabel {color:orange}')
        self.authed_btn = QPushButton('完成', self)
        # noinspection PyUnresolvedReferences
        self.authed_btn.clicked.connect(self._check_auth_and_back)
        self._layout = QVBoxLayout(self)
        # Arrage ui layout
        self.setFixedWidth(300)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.gt_input)
        self._layout.addWidget(self.challenge_input)
        self._layout.addWidget(self.auth_link)
        self._layout.addWidget(self.validate_input)
        self._layout.addWidget(self.seccode_input)
        self._layout.addWidget(self.hint_label)
        self._layout.addWidget(self.authed_btn)

    def _check_auth_and_back(self):
        # todo: use qvalidator
        if self.validate_input.text() == '' or self.seccode_input.text() == '':
            self.hint_label.setText('请输入验证结果')
            return
        # noinspection PyUnresolvedReferences
        self.auth_success.emit(
            self.validate_input.text(), self.seccode_input.text(),
            self.challenge_input.text(), self._token, self.type)
        self.close()

    def _create_link_label(self, link: str, text: str) -> QLabel:
        auth_link = QLabel(self)
        auth_link.setText(f'<a href="{link}">{text}</a>')
        auth_link.setTextFormat(Qt.RichText)
        auth_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        auth_link.setOpenExternalLinks(True)
        return auth_link

    @staticmethod
    def exception_handler(func):
        def inner(*args, **kwargs):
            self = args[0]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                QMessageBox.warning(self, '错误提示', str(e))

        return inner

    @exception_handler
    def request_challenge_params(self, type_: str):
        self.auth_link.setText(f'<a href="#">正在获取验证链接...</a>')
        self.type = type_
        self.validate_input.clear()
        self.seccode_input.clear()
        data = self._provider.request_captcha()
        geetest = data.geetest
        self.gt_input.setText(geetest.gt)
        self.challenge_input.setText(geetest.challenge)
        self._token = data.token
        self.auth_link.setText(
            f'<a href="https://brucezhang1993.github.io/fuo-geetest-validator/?gt={geetest.gt}'
            f'&challenge={geetest.challenge}">点击链接完成验证</a>')


class BLoginDialog(QDialog):
    """
    登录框
    """
    def __init__(self, parent=None, provider=None):
        super(BLoginDialog, self).__init__(parent)
        self._captcha_id = None
        self._provider: BilibiliProvider = provider
        self._tab = QTabWidget(self)
        self.setFixedWidth(300)
        self.setMinimumHeight(200)
        self._tab.setFixedWidth(300)
        # 验证码登录
        self._sms_tab = QFrame(self._tab)
        self.sms_username_input = QLineEdit(self._sms_tab)
        self.sms_username_input.setPlaceholderText("手机号")
        self.sms_send_btn = QPushButton('发送验证码', self._sms_tab)
        self.sms_code_input = QLineEdit(self._sms_tab)
        self.sms_code_input.setPlaceholderText("验证码")
        self.sms_ok_btn = QPushButton('登录', self._sms_tab)
        self._sms_layout = QVBoxLayout(self._sms_tab)
        # Arrage ui layout
        self._sms_layout.setContentsMargins(0, 0, 0, 0)
        self._sms_layout.setSpacing(0)
        self._sms_layout.addWidget(self.sms_username_input)
        self._sms_layout.addWidget(self.sms_send_btn)
        self._sms_layout.addWidget(self.sms_code_input)
        self._sms_layout.addWidget(self.sms_ok_btn)
        # noinspection PyUnresolvedReferences
        self.sms_send_btn.clicked.connect(self._start_auth_code)
        # noinspection PyUnresolvedReferences
        self.sms_ok_btn.clicked.connect(self._start_sms_login)
        # 密码登录
        self._pw_tab = QFrame(self._tab)
        self.username_input = QLineEdit(self._pw_tab)
        self.username_input.setPlaceholderText("账号")
        self.pw_input = QLineEdit(self._pw_tab)
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("密码")
        self.ok_btn = QPushButton('登录', self._pw_tab)
        self._pw_layout = QVBoxLayout(self._pw_tab)
        # Arrage ui layout
        self._pw_layout.setContentsMargins(0, 0, 0, 0)
        self._pw_layout.setSpacing(0)
        self._pw_layout.addWidget(self.username_input)
        self._pw_layout.addWidget(self.pw_input)
        self._pw_layout.addWidget(self.ok_btn)
        self._auth_dialog = BAuthDialog(self, provider)
        # noinspection PyUnresolvedReferences
        self.ok_btn.clicked.connect(self._start_auth)
        self._tab.addTab(self._sms_tab, '验证码登录')
        self._tab.addTab(self._pw_tab, '密码登录')
        # auth back signal
        # noinspection PyUnresolvedReferences
        self._auth_dialog.auth_success.connect(self._auth_back)

    def _start_auth(self):
        self._auth_dialog.setWindowTitle('密码登录验证')
        self._auth_dialog.show()
        self._auth_dialog.request_challenge_params('login')

    def _start_auth_code(self):
        self._auth_dialog.setWindowTitle('发送验证码验证')
        self._auth_dialog.show()
        self._auth_dialog.request_challenge_params('sms')

    @staticmethod
    def exception_handler(func):
        def inner(*args, **kwargs):
            self = args[0]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                QMessageBox.warning(self, '错误提示', str(e))

        return inner

    @exception_handler
    def _start_sms_login(self, _):
        resp = self._provider.sms_code_login(SmsCodeLoginRequest(
            tel=self.sms_username_input.text(),
            code=self.sms_code_input.text(),
            captcha_key=self._captcha_id
        ))
        self.close()

    @exception_handler
    def _continue_password_login(self, validate: str, seccode: str, challenge: str, token: str):
        key_data = self._provider.request_key()
        encrypted_pw = self._get_encrypted_password(key_data)
        resp = self._provider.password_login(PasswordLoginRequest(
            username=self.username_input.text(),
            password=encrypted_pw,
            token=token,
            challenge=challenge,
            validate=validate,
            seccode=seccode
        ))
        if resp.data.status == 2:
            # 需要验证手机号
            QMessageBox.warning(self, '登录提示', '本次登录需要验证手机号，请使用验证码登录')
            self._tab.setCurrentIndex(0)
        else:
            self.close()

    @exception_handler
    def _continue_send_sms(self, validate: str, seccode: str, challenge: str, token: str):
        resp = self._provider.sms_send_code(SendSmsCodeRequest(
            tel=self.sms_username_input.text(),
            token=token,
            challenge=challenge,
            validate=validate,
            seccode=seccode
        ))
        self._captcha_id = resp.data.captcha_key

    def _auth_back(self, validate: str, seccode: str, challenge: str, token: str, type_: str):
        match type_:
            case 'login':
                self._continue_password_login(validate, seccode, challenge, token)
            case 'sms':
                self._continue_send_sms(validate, seccode, challenge, token)

    def _get_encrypted_password(self, key_data: RequestLoginKeyResponse):
        salted_pw = key_data.hash + self.pw_input.text()
        return rsa_encrypt(salted_pw, key_data.key)


class BUiManager:
    def __init__(self, app: GuiApp, provider: BilibiliProvider):
        self._user: Optional[UserModel] = None
        self._provider = provider
        self._app = app
        self._pvd_uimgr: ProviderUiManager = app.pvd_uimgr
        self._pvd_item = self._pvd_uimgr.create_item(
            name=__identifier__,
            text=__alias__,
            symbol='📺',
            desc='点击登录',
            colorful_svg=(Path(__file__).parent / 'assets' / 'icon.svg').as_posix()
        )
        self._pvd_item.clicked.connect(self._login_or_get_user)
        self._pvd_uimgr.add_item(self._pvd_item)
        self.login_dialog = BLoginDialog(None, self._provider)
        # 新建收藏夹
        pl_header = self._app.ui.left_panel.playlists_header
        pl_header.setContextMenuPolicy(Qt.ActionsContextMenu)
        new_pl_action = QAction('新建收藏夹', pl_header)
        pl_header.addAction(new_pl_action)
        # noinspection PyUnresolvedReferences
        new_pl_action.triggered.connect(self.new_playlist)
        self._initial_pages()

    def new_playlist(self):
        name, o1 = QInputDialog.getText(self._app.ui.left_panel.playlists_header, '新建收藏夹', '收藏夹标题')
        if not o1:
            return
        desc, o2 = QInputDialog.getText(self._app.ui.left_panel.playlists_header, '新建收藏夹', '收藏夹简介')
        if not o2:
            return
        privacy, o3 = QInputDialog.getItem(self._app.ui.left_panel.playlists_header, '新建收藏夹', '歌单权限', ['公开', '私有'])
        if not o3:
            return
        try:
            self._provider.user_playlist_new(name, desc, 1 if privacy == '私有' else 0)
        except Exception as e:
            QMessageBox.warning(self._app.ui.left_panel.playlists_header, '新建收藏夹失败', str(e))

    def _initial_pages(self):
        from fuo_bilibili.page_home import render as home_render
        from fuo_bilibili.page_ranking import render as ranking_render
        self._app.browser.route('/providers/bilibili/home')(home_render)
        self._app.browser.route('/providers/bilibili/ranking')(ranking_render)

    async def load_user_content(self):
        left = self._app.ui.left_panel
        left.playlists_con.show()
        left.my_music_con.show()
        # 音乐
        mymusic_home_item = self._app.mymusic_uimgr.create_item('📺 我的首页')
        mymusic_home_item.clicked.connect(
            lambda: self._app.browser.goto(page='/providers/bilibili/home'),
            weak=False)
        mymusic_ranking_item = self._app.mymusic_uimgr.create_item('🔥 全站热门')
        mymusic_ranking_item.clicked.connect(
            lambda: self._app.browser.goto(page='/providers/bilibili/ranking'),
            weak=False
        )
        self._app.mymusic_uimgr.clear()
        self._app.mymusic_uimgr.add_item(mymusic_home_item)
        self._app.mymusic_uimgr.add_item(mymusic_ranking_item)
        # 歌单列表
        self._app.pl_uimgr.clear()
        # 视频区
        special_playlists = self._provider.special_playlists()
        playlists = self._provider.user_playlists(self._user.identifier)
        fav_playlists = self._provider.fav_playlists(self._user.identifier)
        self._app.pl_uimgr.add(special_playlists)
        self._app.pl_uimgr.add(playlists)
        self._app.pl_uimgr.add(fav_playlists, is_fav=True)
        # 音频区
        audio_fav_list = self._provider.audio_favorite_playlists()
        audio_coll_list = self._provider.audio_collected_playlists()
        self._app.pl_uimgr.add(audio_fav_list)
        self._app.pl_uimgr.add(audio_coll_list, is_fav=True)

    def _login(self):
        self._user = self._provider.auth(None)
        asyncio.ensure_future(self.load_user_content())

    def _login_or_get_user(self):
        if self._provider.cookie_check():
            self._login()
            self._pvd_item.text = f'{__alias__}已登录：{self._user.name} UID:{self._user.identifier}'
            return
        self.login_dialog.show()
