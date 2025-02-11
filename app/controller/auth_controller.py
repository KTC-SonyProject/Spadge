import logging

from flet import Page

from app.controller.core import AbstractController
from app.controller.manager.auth_manager import AuthManager
from app.views.auth_view import LoginView, LogoutView, UpdateView
from app.views.core import BannerView

logger = logging.getLogger(__name__)


class AuthController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager, is_errored=False):
        self.page = page
        self.auth_manager = auth_manager
        self.banner = BannerView(page)
        self.is_errored = is_errored  # corrected assignment

    def _login(self, _, user_id="", password=""):
        if self.auth_manager.check_credentials(user_id, password):
            self.page.session.set("is_authenticated", True)
            self.banner.show_banner("success", "ログインしました")
            self.page.go("/home")
        else:
            self.banner.show_banner("error", "IDまたはパスワードが間違っています")

    def get_view(self):
        self.view = LoginView(self.page, self._login, self.is_errored)
        return self.view


class LogoutController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager):
        self.page = page
        self.auth_manager = auth_manager
        self.banner = BannerView(page)

    def _logout(self, _):
        self.page.session.set("is_authenticated", False)
        self.banner.show_banner("success", "ログアウトしました")
        self.page.go("/")

    def get_view(self):
        self.view = LogoutView(self.page, self._logout)
        return self.view


class UpdateController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager):
        self.page = page
        self.auth_manager = auth_manager
        self.banner = BannerView(page)

    def _update(self, _, user_id=None, password=None):
        if not user_id or not password:
            self.banner.show_banner("error", "IDとパスワードを両方入力してください")
            return
        try:
            self.auth_manager.update_credentials(user_id, password)
            self.banner.show_banner("success", "変更されました")
            self.page.go("/settings")
        except ValueError as ve:
            logger.error(f"ValueError updating credentials: {ve}")
            self.banner.show_banner("error", "無効なIDまたはパスワードです")
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            self.banner.show_banner("error", "エラーが発生しました")

    def get_view(self):
        self.now_id = self.auth_manager.credentials.get("id")
        self.view = UpdateView(self.page, self._update, self.now_id)
        return self.view
