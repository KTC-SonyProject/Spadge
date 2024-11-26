from flet import (
    Column,
    Container,
    CrossAxisAlignment,
    Divider,
    FloatingActionButton,
    IconButton,
    Markdown,
    MarkdownExtensionSet,
    NavigationRail,
    NavigationRailDestination,
    NavigationRailLabelType,
    Page,
    Row,
    Text,
    TextButton,
    TextField,
    alignment,
    border_radius,
    colors,
    icons,
    VerticalDivider,
    AlertDialog,
    MainAxisAlignment,
    InputBorder,
    padding,
)

from app.db_conn import DatabaseHandler


class RailDescription(Row):
    def __init__(self, page: Page, title: str, id: int):
        super().__init__()
        self.page = page
        self.title = title
        self.id = id

        self.controls = [
            Text(self.title),
            IconButton(icon=icons.EDIT_NOTE, tooltip="Edit Documents", on_click=self.click),
        ]

    def click(self, e):
        self.page.go(f"/documents/{self.id}/edit")



class Sidebar(Container):
    def __init__(self, page:Page, documents_list: list):
        super().__init__()
        self.page = page
        self.db = DatabaseHandler(self.page.data["settings"]())

        self.nav_rail_visible = True
        self.nav_rail_items = []
        for document in documents_list:
            self.nav_rail_items.append(
                NavigationRailDestination(
                    label_content=RailDescription(self.page, document[1], document[0]),
                    label=document[1],
                    selected_icon=icons.CHEVRON_RIGHT_ROUNDED,
                    icon=icons.CHEVRON_RIGHT_OUTLINED,
                    )
                )

        self.nav_rail = NavigationRail(
            selected_index=None,
            label_type=NavigationRailLabelType.ALL,
            # min_width=100,
            leading=FloatingActionButton(icon=icons.CREATE, text="ADD", on_click=self.open_modal),
            group_alignment=-0.9,
            destinations=self.nav_rail_items,
            on_change=self.tap_nav_icon,
            expand=True,
            extended=True,
        )
        self.toggle_nav_rail_button = IconButton(
            icon=icons.ARROW_CIRCLE_LEFT,
            icon_color=colors.BLUE_GREY_400,
            selected=False,
            selected_icon=icons.ARROW_CIRCLE_RIGHT,
            on_click=self.toggle_nav_rail,
            tooltip="Collapse Nav Bar",
        )
        self.visible = self.nav_rail_visible

        self.dlg_modal = AlertDialog(
            modal=True,
            inset_padding=padding.symmetric(vertical=40, horizontal=100),
            title=Text("Alert"),
            content=TextField(
                label="タイトル名",
                border=InputBorder.UNDERLINE,
                filled=True,
                hint_text="Enter title name here",
            ),
            actions=[
                TextButton(text="Yes", on_click=self.modal_yes_action),
                TextButton(text="No", on_click=self.modal_no_action),
            ],
            actions_alignment=MainAxisAlignment.END,
        )

        self.content = Row(
            controls=[
                self.nav_rail,
                Container(
                    bgcolor=colors.BLACK26,
                    border_radius=border_radius.all(30),
                    # height=480,
                    alignment=alignment.center_right,
                    width=2
                ),
                self.toggle_nav_rail_button,
            ],
            vertical_alignment=CrossAxisAlignment.START,
        )

    def toggle_nav_rail(self, e):
        self.nav_rail.visible = not self.nav_rail.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.toggle_nav_rail_button.tooltip = (
            "Open Side Bar" if self.toggle_nav_rail_button.selected else "Collapse Side Bar"
        )
        self.update()

    def tap_nav_icon(self, e):
        document_id = e.control.selected_index + 1
        self.page.go(f"/documents/{document_id}")

    def open_modal(self, e):
        e.control.page.overlay.append(self.dlg_modal)
        self.dlg_modal.open = True
        e.control.page.update()

    def modal_yes_action(self, e):
        try:
            if self.dlg_modal.content.value == "":
                raise Exception("タイトル名が入力されていません")
            self.db.connect()
            self.db.execute_query(
                "INSERT INTO documents (title, content) VALUES (%s, %s)",
                (self.dlg_modal.content.value, "")
            )
            result = self.db.fetch_query("SELECT document_id FROM documents ORDER BY created_at DESC LIMIT 1;")
            print(result)
            self.db.close_connection()
            self.dlg_modal.open = False
            self.page.go(f"/documents/{result[0][0]}/edit")
        except Exception as error:
            print(error)
            self.dlg_modal.content.error_text = str(error)
            e.control.page.update()


    def modal_no_action(self, e):
        self.dlg_modal.open = False
        e.control.page.update()
        print("No clicked")


class DocumentBody(Container):
    def __init__(self, page: Page, content: str = ""):
        super().__init__()
        self.page = page
        self.expand = True
        self.alignment=alignment.top_left
        # self.spacing = 10
        self.content_value = content

        self.content = Column(
            controls=[
                Markdown(
                    value=self.content_value,
                    selectable=True,
                    extension_set=MarkdownExtensionSet.GITHUB_WEB,
                    on_tap_link=lambda e: self.page.launch_url(e.data),
                ),
            ],
            scroll="hidden",
        )


class DocumentsBody(Row):
    def __init__(self, page: Page, document_id: int = 0):
        super().__init__()
        self.page = page
        self.vertical_alignment = CrossAxisAlignment.START
        self.expand = True



        self.settings = self.page.data["settings"]()
        self.db = DatabaseHandler(self.settings)

        self.documents_list = self.get_document_list()

        if document_id == 0:
            self.controls = [
                Sidebar(self.page, documents_list=self.documents_list),
                Text("test."),
            ]
        else:
            self.document_body = self.get_document_body(document_id)
            content = self.document_body[2] if self.document_body else "Document not found."
            self.controls = [
                Sidebar(self.page, documents_list=self.documents_list),
                DocumentBody(self.page, content=content),
            ]

    def get_document_body(self, document_id: int):
        self.db.connect()
        result = self.db.fetch_query("SELECT * FROM documents WHERE document_id = %s", (document_id,))
        self.db.close_connection()
        return result[0] if result != [] else None

    def get_document_list(self):
        self.db.connect()
        result = self.db.fetch_query("SELECT document_id, title FROM documents ORDER BY document_id ASC;")
        self.db.close_connection()
        return result




class EditBody(Row):
    def __init__(self, page: Page, document_id: int):
        super().__init__()
        self.page = page
        self.vertical_alignment = CrossAxisAlignment.START
        self.expand = True

        self.settings = self.page.data["settings"]()
        self.db = DatabaseHandler(self.settings)

        self.document = self.get_document_body(document_id)

        self.text_field = TextField(
            value=self.document[2],
            multiline=True,
            expand=True,
            border_color=colors.TRANSPARENT,
            on_change=self.update_preview,
        )
        self.document_body = DocumentBody(self.page, content=self.text_field.value)

        self.controls = [
            self.text_field,
            VerticalDivider(color=colors.BLUE_GREY_400),
            self.document_body,
        ]

    def get_document_body(self, document_id: int):
        self.db.connect()
        result = self.db.fetch_query("SELECT * FROM documents WHERE document_id = %s", (document_id,))
        self.db.close_connection()
        return result[0] if result != [] else None

    def update_preview(self, e):
        # self.document_body.content_value = self.text_field.value
        self.document_body.content.controls[0].value = self.text_field.value
        self.document_body.update()
        self.update()
        self.page.update()

class EditDocumentBody(Column):
    def __init__(self, page: Page, document_id: int):
        super().__init__()
        self.page = page
        self.expand = True
        self.horizontal_alignment = CrossAxisAlignment.CENTER
        self.spacing = 10

        self.db = DatabaseHandler(self.page.data["settings"]())

        self.document_id = document_id

        self.controls = [
            Row(
                controls=[
                    IconButton(icon=icons.ARROW_BACK, on_click=self.back_page, tooltip="Back"),
                    TextButton(text="Save", on_click=self.save_document, icon=icons.SAVE),
                ],
                alignment=alignment.center_left,
            ),
            Divider(color=colors.BLUE_GREY_400),
            EditBody(self.page, self.document_id),
        ]

    def back_page(self, e):
        self.page.go(f"/documents/{self.document_id}")

    def save_document(self, e):
        self.db.connect()
        self.db.execute_query(
            "UPDATE documents SET content = %s WHERE document_id = %s",
            (self.controls[2].text_field.value, self.document_id)
        )
        self.db.close_connection()
        self.page.go(f"/documents/{self.document_id}")

