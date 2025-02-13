import logging
import os

from flet import FilePicker, FilePickerResultEvent, FilePickerUploadFile, InputBorder, Page, TextButton, TextField

from app.ai.vector_db import delete_document_from_vectorstore, indexing_document
from app.controller.core import AbstractController
from app.controller.manager import (
    AuthManager,
    DocumentsManager,
)
from app.controller.utils import markitdown
from app.views.core import BannerView
from app.views.documents_view import (
    DocumentsView,
    EditBody,
    EditDocumentsView,
    Sidebar,
    create_add_doc_modal,
    create_edit_doc_modal,
    create_markitdown_file_modal,
    create_markitdown_modal,
    create_markitdown_url_modal,
    create_nav_rail_item,
)

logger = logging.getLogger(__name__)


class DocumentsSidebarController(AbstractController):
    def __init__(self, page: Page, docs_manager: DocumentsManager, is_authenticated: bool = False):
        super().__init__(page)
        self.manager = docs_manager
        self.is_authenticated = is_authenticated
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
                    self.is_authenticated,
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
            self.is_authenticated,
        )
        wrap_width = 800
        if self.page.window.width < wrap_width:
            self.sidebar.nav_rail.visible = False
        return self.sidebar


class DocumentsController(AbstractController):
    def __init__(
        self,
        page: Page,
        docs_manager: DocumentsManager,
        auth_manager: AuthManager,
        document_id: int | None = None,
        is_edit: bool = False,
    ):
        super().__init__(page)
        self.manager = docs_manager
        self.auth_manager = auth_manager
        self.is_authenticated = self.auth_manager.check_is_authenticated()
        self.docs_view = None
        self.edit_body = None
        self.edit_view = None
        self.sidebar = None
        self.edit_doc_modal = None
        self.banner = BannerView(page)
        self.docs_sidebar_controller = DocumentsSidebarController(page, docs_manager, self.is_authenticated)
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

    def _create_markitdown_url_modal(self):
        def no_func(_):
            self.markitdown_url_modal.open = False
            self.page.update()

        def yes_func(_):
            url = markitdown_field.value
            logger.debug(f"URL: {url}")
            try:
                doc = markitdown(url)
            except Exception as e:
                logger.error(f"Error converting markdown: {e}")
                doc = "Error converting markdown."
            self.edit_body.text_field.value = doc
            self.edit_body.document_body.preview_content.value = doc
            self.markitdown_url_modal.open = False
            self.edit_body.update()
            self.page.update()

        markitdown_field = TextField(
            label="url",
            border=InputBorder.UNDERLINE,
            hint_text="Enter url here",
            filled=True,
        )
        self.markitdown_url_modal = create_markitdown_url_modal(markitdown_field, yes_func, no_func)
        self.page.overlay.append(self.markitdown_url_modal)
        self.markitdown_url_modal.open = True
        self.page.update()
        return self.markitdown_url_modal

    def _create_markitdown_file_modal(self):
        def run_markitdown(name):
            try:
                url = f"/app/app/storage/temp/uploads/{name}"
                doc = markitdown(url)
                os.remove(url)
            except Exception as e:
                logger.error(f"Error converting markdown: {e}")
                doc = "Error converting markdown."
            self.edit_body.text_field.value = doc
            self.edit_body.document_body.preview_content.value = doc
            self.markitdown_file_modal.open = False
            self.edit_body.update()
            self.page.update()

        def on_upload(e):
            if e.progress == 1.0:
                run_markitdown(e.file_name)

        def upload_files(e):
            upload_list = []
            if file_picker.result is not None and file_picker.result.files is not None:
                for f in file_picker.result.files:
                    upload_list.append(
                        FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f.name, 600),
                        )
                    )
                file_picker.upload(upload_list)

        def on_dialog_result(e: FilePickerResultEvent):
            upload_files(e)

        def no_func(_):
            self.markitdown_file_modal.open = False
            self.page.update()

        def wrap_pick_files():
            self.markitdown_file_modal.open = False
            file_picker.pick_files(allowed_extensions=["pptx", "docx", "pdf"])

        file_picker = FilePicker(on_result=on_dialog_result, on_upload=on_upload)
        self.page.overlay.append(file_picker)
        self.page.update()

        self.content = "選択したファイルからマークダウンを生成します"
        self.markitdown_file_modal = create_markitdown_file_modal(self.content, wrap_pick_files, no_func)
        self.page.overlay.append(self.markitdown_file_modal)
        self.markitdown_file_modal.open = True
        self.page.update()

    def _create_markitdown_modal(self):
        def no_func(_):
            self.markitdown_modal.open = False
            self.page.update()

        def url_func(_):
            self.markitdown_modal.open = False
            self._create_markitdown_url_modal()
            self.page.update()

        def file_func(_):
            self.markitdown_modal.open = False
            self._create_markitdown_file_modal()
            self.page.update()

        markitdown_url = TextButton("URLから", on_click=url_func)
        markitdown_file = TextButton("ファイルから", on_click=file_func)
        self.markitdown_modal = create_markitdown_modal([markitdown_url, markitdown_file], no_func)
        return self.markitdown_modal

    def open_markitdown_modal(self, _):
        self.page.overlay.append(self._create_markitdown_modal())
        self.markitdown_modal.open = True
        self.page.update()

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
        if self.is_edit and self.is_authenticated:
            self.edit_body = EditBody(
                self.page,
                self._update_preview,
                doc["content"],
            )
            self.edit_view = EditDocumentsView(
                self.document_id,
                self.edit_body,
                self._open_modal,
                self.open_markitdown_modal,
                self._save_document,
                self._delete_document,
                doc["title"],
            )
            return self.edit_view
        else:
            self.docs_view = DocumentsView(self.page, self.sidebar, doc["content"])
            return self.docs_view
