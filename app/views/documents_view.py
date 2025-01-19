import logging

from flet import (
    AlertDialog,
    ButtonStyle,
    Colors,
    Column,
    Container,
    Control,
    CrossAxisAlignment,
    Divider,
    ElevatedButton,
    FloatingActionButton,
    IconButton,
    Icons,
    InputBorder,
    MainAxisAlignment,
    Markdown,
    MarkdownExtensionSet,
    NavigationRail,
    NavigationRailDestination,
    NavigationRailLabelType,
    Page,
    RoundedRectangleBorder,
    Row,
    ScrollMode,
    Text,
    TextButton,
    TextField,
    TextOverflow,
    VerticalDivider,
    alignment,
    border_radius,
    padding,
)

logger = logging.getLogger(__name__)


def create_rail_description(page: Page, title: str, id: int):
    return Row(
        expand=True,
        alignment=MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            Text(title, width=150, max_lines=1, overflow=TextOverflow.ELLIPSIS),
            IconButton(
                icon=Icons.EDIT_NOTE,
                tooltip="Edit Documents",
                on_click=lambda _: page.go(f"/documents/{id}/edit"),
            ),
        ],
    )


def create_nav_rail_item(page: Page, title: str, id: int):
    return NavigationRailDestination(
        label_content=create_rail_description(page, title, id),
        label=title,
        selected_icon=Icons.CHEVRON_RIGHT_ROUNDED,
        icon=Icons.CHEVRON_RIGHT_OUTLINED,
        data=id,
    )


def create_modal(
    title: Control,
    content: Control,
    actions: list[Control],
    actions_alignment: MainAxisAlignment = MainAxisAlignment.END,
):
    return AlertDialog(
        modal=True,
        inset_padding=padding.symmetric(vertical=40, horizontal=100),
        title=title,
        content=content,
        actions=actions,
        actions_alignment=actions_alignment,
    )


def create_add_doc_modal(content: TextField, modal_yes_action: callable, modal_no_action: callable):
    return create_modal(
        title=Text("新規追加"),
        content=content,
        actions=[
            TextButton(text="Yes", on_click=modal_yes_action),
            TextButton(text="No", on_click=modal_no_action),
        ],
    )


def create_edit_doc_modal(save_document: callable, not_save_action: callable, cancel_action: callable):
    return create_modal(
        title=Text("※注意※", color=Colors.RED),
        content=Text("ドキュメントの変更内容を保存せずに戻りますか？"),
        actions=[
            ElevatedButton(
                text="保存して戻る",
                style=ButtonStyle(
                    shape=RoundedRectangleBorder(radius=10),
                ),
                on_click=save_document,
            ),
            TextButton(text="保存せずに戻る", on_click=not_save_action),
            TextButton(text="変更を続ける", on_click=cancel_action),
        ],
        actions_alignment=MainAxisAlignment.CENTER,
    )


class Sidebar(Container):
    def __init__(
        self,
        nav_rail_items: list[NavigationRailDestination],
        open_modal: callable,
        tap_nav_icon: callable,
        toggle_nav_rail: callable,
    ):
        super().__init__(
            # expand=True,
            visible=True,
        )
        self.nav_rail_visible = True
        self.nav_rail_items = nav_rail_items
        self.nav_rail = NavigationRail(
            # min_extended_width=50,
            # min_width=20,
            selected_index=None,
            label_type=NavigationRailLabelType.ALL,
            leading=FloatingActionButton(icon=Icons.CREATE, text="ADD DOCUMENT", on_click=open_modal),
            group_alignment=-0.9,
            destinations=self.nav_rail_items,
            on_change=tap_nav_icon,
            expand=True,
            extended=True,
        )
        self.toggle_nav_rail_button = IconButton(
            icon=Icons.ARROW_CIRCLE_LEFT,
            icon_color=Colors.BLUE_GREY_400,
            selected=False,
            selected_icon=Icons.ARROW_CIRCLE_RIGHT,
            on_click=toggle_nav_rail,
            tooltip="Collapse Nav Bar",
        )

        self.content = Row(
            controls=[
                self.nav_rail,
                Container(
                    bgcolor=Colors.BLACK26,
                    border_radius=border_radius.all(30),
                    alignment=alignment.center_right,
                    width=2,
                ),
                self.toggle_nav_rail_button,
            ],
            vertical_alignment=CrossAxisAlignment.START,
        )


class DocumentBody(Container):
    def __init__(self, page: Page, content: str = ""):
        super().__init__(
            expand=True,
            alignment=alignment.top_left,
        )
        self.page = page
        self.preview_content = Markdown(
            value=content,
            selectable=True,
            extension_set=MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: self.page.launch_url(e.data),
        )

        self.content = Column(
            controls=[
                self.preview_content,
            ],
            expand=True,
            scroll=ScrollMode.HIDDEN,
        )


class DocumentsView(Row):
    def __init__(self, page: Page, sidebar: Sidebar, content: str):
        super().__init__(
            expand=True,
            vertical_alignment=CrossAxisAlignment.START,
        )
        self.sidebar = sidebar
        self.content = content

        self.controls = [
            self.sidebar,
            DocumentBody(page, self.content),
        ]


class EditBody(Row):
    def __init__(self, page: Page, update_preview: callable, content: str = ""):
        super().__init__(
            expand=True,
            vertical_alignment=CrossAxisAlignment.START,
        )
        self.text_field = TextField(
            value=content,
            multiline=True,
            expand=True,
            border_color=Colors.TRANSPARENT,
            on_change=update_preview,
            hint_text="Document here...",
        )
        self.document_body = DocumentBody(page, content=content)

        self.controls = [
            self.text_field,
            VerticalDivider(color=Colors.BLUE_GREY_400),
            self.document_body,
        ]


class EditDocumentsView(Column):
    def __init__(
        self,
        doc_id: int,
        edit_body: EditBody,
        open_modal: callable,
        save_document: callable,
        delete_document: callable,
        title: str = "Untitle",
    ):
        super().__init__(
            expand=True,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self.doc_id = doc_id

        self.edit_body = edit_body
        self.title_field = TextField(
            value=title,
            border=InputBorder.UNDERLINE,
        )

        self.controls = [
            Row(
                controls=[
                    Row(
                        controls=[
                            IconButton(icon=Icons.ARROW_BACK, on_click=open_modal, tooltip="Back"),
                            self.title_field,
                        ],
                    ),
                    Row(
                        controls=[
                            TextButton(text="Save", on_click=save_document, icon=Icons.SAVE),
                            TextButton(text="Delete", on_click=delete_document, icon=Icons.DELETE),
                        ],
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Divider(color=Colors.BLUE_GREY_400),
            self.edit_body,
        ]
