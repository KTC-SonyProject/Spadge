import logging

from flet import InputBorder, Page, TextField

from app.ai.vector_db import delete_document_from_vectorstore, indexing_document
from app.controller.core import AbstractController
from app.controller.manager.documents_manager import DocumentsManager
from app.views.core import BannerView
from app.views.documents_view import (
    DocumentsView,
    EditBody,
    EditDocumentsView,
    Sidebar,
    create_add_doc_modal,
    create_edit_doc_modal,
    create_nav_rail_item,
)

logger = logging.getLogger(__name__)


class DocumentsSidebarController(AbstractController):
    def __init__(self, page: Page, docs_manager: DocumentsManager):
        super().__init__(page)
        self.manager = docs_manager
        self.banner = BannerView(page)
        self.add_doc_modal = None

    def _add_document(self, _, add_doc_title_field: TextField):
        title = add_doc_title_field.value
        if not title:
            logger.warning("Title is empty.")
            self.banner.show_banner("error", "Title is empty.")
            return
        try:
            create_doc_id = self.manager.add_document(title)
            self.add_doc_modal.open = False
            self.page.go(f"/documents/{create_doc_id}/edit")
        except Exception as err:
            logger.error(f"Error adding document: {err}")
            self.banner.show_banner("error", "Error adding document.")

    def _create_nav_rail_item(self):
        items = []
        documents_list = self.manager.get_all_documents()
        for doc in documents_list:
            items.append(
                create_nav_rail_item(
                    self.page,
                    doc["title"],
                    doc["id"],
                )
            )
        return items

    def _create_add_doc_modal(self):
        def no_action(_):
            self.add_doc_modal.open = False
            self.page.update()

        add_doc_title_field = TextField(
            label="タイトル名",
            border=InputBorder.UNDERLINE,
            hint_text="Enter title name here",
            filled=True,
        )
        self.add_doc_modal = create_add_doc_modal(
            add_doc_title_field,
            lambda e: self._add_document(e, add_doc_title_field),
            no_action,
        )
        return self.add_doc_modal

    def _open_modal(self, e):
        self.page.overlay.append(self._create_add_doc_modal())
        self.add_doc_modal.open = True
        self.page.update()

    def _tap_nav_icon(self, e):
        selected_index = e.control.selected_index
        doc_id = e.control.destinations[selected_index].data
        self.page.go(f"/documents/{doc_id}")

    def _toggle_nav_rail(self, _):
        self.sidebar.nav_rail.visible = not self.sidebar.nav_rail.visible
        self.sidebar.toggle_nav_rail_button.selected = not self.sidebar.toggle_nav_rail_button.selected
        self.sidebar.toggle_nav_rail_button.tooltip = (
            "Open Side Bar" if self.sidebar.toggle_nav_rail_button.selected else "Collapse Side Bar"
        )
        self.page.update()

    def get_view(self):
        self.sidebar = Sidebar(
            self._create_nav_rail_item(),
            self._open_modal,
            self._tap_nav_icon,
            self._toggle_nav_rail,
        )
        wrap_width = 800
        if self.page.window.width < wrap_width:
            self.sidebar.nav_rail.visible = False
        return self.sidebar


class DocumentsController(AbstractController):
    def __init__(
        self, page: Page, docs_manager: DocumentsManager, document_id: int | None = None, is_edit: bool = False
    ):
        super().__init__(page)
        self.manager = docs_manager
        self.docs_view = None
        self.edit_body = None
        self.edit_view = None
        self.sidebar = None
        self.edit_doc_modal = None
        self.banner = BannerView(page)
        self.docs_sidebar_controller = DocumentsSidebarController(page, docs_manager)
        self.document_id = document_id
        self.is_edit = is_edit

    def _back_page(self, _):
        if self.edit_doc_modal:
            self.edit_doc_modal.open = False
        self.page.go(f"/documents/{self.document_id}")

    def _save_document(self, _):
        if self.edit_view:
            title = self.edit_view.title_field.value
            content = self.edit_view.edit_body.text_field.value
            try:
                self.manager.update_document(self.document_id, title, content)
                indexing_document(content, self.document_id)
                self._back_page(_)
            except Exception as err:
                logger.error(f"Error saving document: {err}")
                self.banner.show_banner("error", "Error saving document.")
        else:
            logger.error("No edit view found.")

    def _delete_document(self, _):
        if self.edit_view:
            try:
                self.manager.delete_document(self.document_id)
                delete_document_from_vectorstore(self.document_id)
                self.page.go("/documents")
                self.banner.show_banner("success", "Document deleted successfully.")
            except Exception as err:
                logger.error(f"Error deleting document: {err}")
                self.banner.show_banner("error", "Error deleting document.")
        else:
            logger.error("No edit view found.")

    def _create_edit_doc_modal(self):
        def cancel_action(_):
            self.edit_doc_modal.open = False
            self.page.update()

        self.edit_doc_modal = create_edit_doc_modal(
            self._save_document,
            self._back_page,
            cancel_action,
        )
        return self.edit_doc_modal

    def _open_modal(self, e):
        self.page.overlay.append(self._create_edit_doc_modal())
        self.edit_doc_modal.open = True
        self.page.update()

    def _update_preview(self, e):
        self.edit_body.document_body.preview_content.value = e.control.value
        # self.edit_body.document_body.preview_content.update()
        self.edit_body.update()
        # self.page.update()

    def get_view(self) -> DocumentsView:
        self.sidebar = self.docs_sidebar_controller.get_view()
        if not self.document_id:
            self.docs_view = DocumentsView(
                self.page,
                self.sidebar,
                "No document selected.",
            )
            return self.docs_view

        doc = self.manager.get_document_by_id(self.document_id)
        if self.is_edit:
            self.edit_body = EditBody(
                self.page,
                self._update_preview,
                doc["content"],
            )
            self.edit_view = EditDocumentsView(
                self.document_id,
                self.edit_body,
                self._open_modal,
                self._save_document,
                self._delete_document,
                doc["title"],
            )
            return self.edit_view
        else:
            self.docs_view = DocumentsView(self.page, self.sidebar, doc["content"])
            return self.docs_view
