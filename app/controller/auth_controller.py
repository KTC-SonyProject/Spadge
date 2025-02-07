import logging

from flet import Page

from app.controller.core import AbstractController
from app.controller.manager.auth_manager import AuthManager
from app.views.auth_view import AuthView, LogoutView
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
            self.page.go("/settings")
        else:
            self.banner.show_banner("error", "IDまたはパスワードが間違っています")

    def get_view(self):
        self.view = AuthView(self.page, self._login, self.is_errored)
        return self.view


class LogoutController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager):
        self.page = page
        self.auth_manager = auth_manager

    def _logout(self, _):
        self.page.session.set("is_authenticated", False)
        self.page.go("/")

    def get_view(self):
        self.view = LogoutView(self.page, self._logout)
        return self.view
