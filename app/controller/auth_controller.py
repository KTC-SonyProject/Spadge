import logging

from flet import Page

from app.controller.core import AbstractController
from app.controller.manager.auth_manager import AuthManager
from app.views.auth_view import AuthView
from app.views.core import BannerView

logger = logging.getLogger(__name__)


class AuthController(AbstractController):
    def __init__(self, page: Page, auth_manager: AuthManager):
        self.page = page
        self.auth_manager = auth_manager
        self.banner = BannerView(page)

    def _login(self, _, user_id="", password=""):
        if self.auth_manager.check_credentials(user_id, password):
            self.page.session.set("is_authenticated", True)
            self.page.go("/settings")
        else:
            self.banner.show_banner("error", "Invalid credentials")

    def get_view(self):
        self.view = AuthView(self.page, self._login)
        return self.view
