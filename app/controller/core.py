import logging

from flet import (
    ControlEvent,
    Page,
)

logger = logging.getLogger(__name__)


def go_page(page: Page, path: str) -> callable:
    def handler(_: ControlEvent):
        page.go(path)
    return handler
