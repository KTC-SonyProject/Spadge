import logging
from abc import ABC, abstractmethod

from flet import (
    ControlEvent,
    Page,
)

logger = logging.getLogger(__name__)


class AbstractController(ABC):
    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    def get_view(self) -> callable:
        raise NotImplementedError

def go_page(page: Page, path: str) -> callable:
    def handler(_: ControlEvent):
        page.go(path)
    return handler
