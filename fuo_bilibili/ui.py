import asyncio
import base64
import logging
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QPushButton, QLabel
from feeluown.app.gui_app import GuiApp
from feeluown.gui import ProviderUiManager

from fuo_bilibili import __identifier__, __alias__, BilibiliProvider
from fuo_bilibili.api.schema.requests import PasswordLoginRequest
from fuo_bilibili.api.schema.responses import RequestLoginKeyResponse
from fuo_bilibili.util import rsa_encrypt

logger = logging.getLogger(__name__)


class BAuthDialog(QDialog):
    """
    人机验证
    """
    # signal: validate, seccode, challenge, token
    auth_success = pyqtSignal(str, str, str, str)

    def __init__(self, parent=None, provider: BilibiliProvider=None):
        super(BAuthDialog, self).__init__(parent)
        self._token = None
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
            self.challenge_input.text(), self._token)
        self.close()

    def _create_link_label(self, link: str, text: str) -> QLabel:
        auth_link = QLabel(self)
        auth_link.setText(f'<a href="{link}">{text}</a>')
        auth_link.setTextFormat(Qt.RichText)
        auth_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        auth_link.setOpenExternalLinks(True)
        return auth_link

    def request_challenge_params(self):
        data = self._provider.request_captcha()
        geetest = data.geetest
        self.gt_input.setText(geetest.gt)
        self.challenge_input.setText(geetest.challenge)
        self._token = data.token
        self.auth_link.setText(f'<a href="https://brucezhang1993.github.io/fuo-geetest-validator/?gt={geetest.gt}&challenge={geetest.challenge}">点击链接完成验证</a>')


class BLoginDialog(QDialog):
    """
    登录框
    """
    def __init__(self, parent=None, provider=None):
        super(BLoginDialog, self).__init__(parent)
        self._provider: BilibiliProvider = provider
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("账号")
        self.pw_input = QLineEdit(self)
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("密码")
        self.ok_btn = QPushButton('登录', self)
        self._layout = QVBoxLayout(self)
        # Arrage ui layout
        self.setFixedWidth(200)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.username_input)
        self._layout.addWidget(self.pw_input)
        self._layout.addWidget(self.ok_btn)
        self._auth_dialog = BAuthDialog(self, provider)
        # connects
        # noinspection PyUnresolvedReferences
        self.ok_btn.clicked.connect(self._start_auth)
        # noinspection PyUnresolvedReferences
        self._auth_dialog.auth_success.connect(self._auth_back)

    def _start_auth(self):
        self._auth_dialog.request_challenge_params()
        self._auth_dialog.show()

    def _auth_back(self, validate: str, seccode: str, challenge: str, token: str):
        key_data = self._provider.request_key()
        encrypted_pw = self._get_encrypted_password(key_data)
        self._provider.password_login(PasswordLoginRequest(
            username=self.username_input.text(),
            password=encrypted_pw,
            token=token,
            challenge=challenge,
            validate=validate,
            seccode=seccode
        ))
        self.close()

    def _get_encrypted_password(self, key_data: RequestLoginKeyResponse):
        salted_pw = key_data.hash + self.pw_input.text()
        return rsa_encrypt(salted_pw, key_data.key)


class BUiManager:
    def __init__(self, app: GuiApp, provider: BilibiliProvider):
        self._user = None
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

    async def _login_as(self, user):
        self._provider.auth(user)
        self._user = user

    def _login_or_get_user(self):
        if self._user is not None:
            asyncio.ensure_future(self._login_as(self._user))
            return
        self.login_dialog.show()
