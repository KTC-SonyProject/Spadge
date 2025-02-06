from flet import (
    Colors,
    Column,
    Container,
    CrossAxisAlignment,
    ElevatedButton,
    Icon,
    Icons,
    Image,
    ImageFit,
    LinearGradient,
    MainAxisAlignment,
    Page,
    Row,
    ScrollMode,
    Text,
    TextAlign,
    alignment,
    app,
)


def create_hero_section(page: Page, scroll_to_step_section: callable):
    """メインビジュアル（ヒーローセクション）"""
    return Container(
        content=Column(
            controls=[
                Column(
                    controls=[
                        Text("ヒトとヒト、コトとヒトを繋ぐ", size=30, weight="bold", color=Colors.WHITE),
                        Text("Connecting People to People, Things to People", size=15, color=Colors.GREY),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                Column(
                    controls=[
                        Text("SRD × AI で、リアルな体験をもっと身近に。", size=20, color=Colors.WHITE),
                        Row(
                            controls=[
                                ElevatedButton(
                                    text="体験する",
                                    bgcolor=Colors.BLUE,
                                    color=Colors.WHITE,
                                    on_click=lambda _: page.go("/home"),
                                ),
                                ElevatedButton(
                                    text="使い方を知る",
                                    bgcolor=Colors.WHITE,
                                    color=Colors.BLUE,
                                    on_click=scroll_to_step_section,
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                Text(" ", size=20, color=Colors.WHITE),
                Row(
                    controls=[
                        Image(
                            src="icon.png",
                            width=150,
                            height=150,
                            fit=ImageFit.COVER,
                        ),
                        Column(
                            controls=[
                                Text("Spatial × Bridge", size=20, color=Colors.GREY, font_family="icon-stentiga"),
                                Text(
                                    "SPADGE",
                                    size=75,
                                    color=Colors.WHITE,
                                    font_family="icon-stentiga",
                                ),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=50,
        ),
        alignment=alignment.center,
        padding=40,
        height=600,
        expand=True,
        gradient=LinearGradient(
            begin=alignment.top_center, end=alignment.bottom_center, colors=[Colors.BLUE, Colors.BLUE_GREY]
        ),
    )


def create_feature_content(icon: Icons, title: str, description: str, color: Colors):
    """機能紹介コンテンツ"""
    return Container(
        content=Column(
            controls=[
                Icon(icon, size=50, color=color),
                Text(title, size=18, weight="bold"),
                Text(description, size=14, color=Colors.BLUE_GREY),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            width=200,
        ),
        padding=10,
    )


def create_feature_section():
    """このアプリでできること（機能紹介セクション）"""
    feature_contents = [
        create_feature_content(
            Icons.PLAY_CIRCLE_FILL, "動画から\n3Dモデルを簡単作成", "スマホで撮影するだけ", Colors.BLUE
        ),
        create_feature_content(Icons.SMART_TOY, "解説をグローバルに", "生成AIで多言語化", Colors.GREEN),
        create_feature_content(
            Icons.DISPLAY_SETTINGS, "SRDで\nリアルな展示を実現", "その場でリアル体験", Colors.PURPLE
        ),
    ]
    return Container(
        content=Column(
            controls=[
                Text("このアプリでできること", size=30, weight="bold"),
                Row(
                    controls=feature_contents,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=40,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


def create_usage_card(title: str, subtitle: str, img_url: str):
    """活用シーンカード"""
    return Container(
        content=Column(
            controls=[
                Image(src=img_url, width=150, height=100, fit=ImageFit.COVER),
                Text(title, size=16, weight="bold"),
                Text(subtitle, size=14, color=Colors.BLUE_GREY),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        border_radius=10,
        bgcolor=Colors.WHITE,
        padding=10,
        margin=10,
    )


def create_usage_section():
    """活用シーン（カード形式 or スライダー表示）"""
    usage_cards = [
        create_usage_card("美術館・文化財保存", "3Dで貴重な資料を残す", "https://via.placeholder.com/150"),
        create_usage_card("商品展示・商談", "リアルなサイネージ", "https://via.placeholder.com/150"),
        create_usage_card("教育・研究", "3Dで学ぶ新しい方法", "https://via.placeholder.com/150"),
        create_usage_card("クリエイター支援", "作品を3Dで共有", "https://via.placeholder.com/150"),
    ]
    return Container(
        content=Column(
            controls=[
                Text("活用シーン", size=24, weight="bold"),
                Row(
                    controls=usage_cards,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


def create_step_widget(step_number: int, description: str):
    """ステップ表示ウィジェット"""
    return Container(
        content=Column(
            controls=[
                Container(
                    content=Text(f"{step_number}", size=20, weight="bold", color=Colors.WHITE),
                    width=40,
                    height=40,
                    alignment=alignment.center,
                    bgcolor=Colors.BLUE,
                    border_radius=20,
                ),
                Text(f"Step {step_number}", size=16, weight="bold"),
                Text(description, size=14, color=Colors.BLUE_GREY, text_align=TextAlign.CENTER),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            width=150,
        ),
        padding=10,
    )


def create_step_section():
    """使い方（ステップ表示）"""
    step_widgets = [
        create_step_widget(1, "動画をアップロード or 外部アプリからインポート"),
        create_step_widget(2, "3Dモデルを管理"),
        create_step_widget(3, "SRDで展示開始！"),
        create_step_widget(4, "AIで解説"),
    ]
    return Container(
        content=Column(
            controls=[
                Text("使い方", size=24, weight="bold"),
                Row(
                    controls=step_widgets,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        padding=20,
        key="step_section",
    )


def create_achievement_card(title: str, description: str):
    """実績セクション"""
    return Container(
        content=Column(
            controls=[
                Text(title, size=16, weight="bold"),
                Text(f"「{description}」", size=14, color=Colors.BLUE_GREY),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        border_radius=10,
        bgcolor=Colors.WHITE,
        padding=10,
        margin=10,
    )


def create_achievement_section():
    """実績（カード形式 or スライダー表示）"""
    achievement_cards = [
        create_achievement_card("SONY様提供産学連携プロジェクト", "テクノロジー賞 受賞"),
        create_achievement_card("学内ROBOT展示", "学内にあるROBOTや学生作品を展示中"),
    ]
    return Container(
        content=Column(
            controls=[
                Text("実績・導入事例", size=24, weight="bold"),
                Row(
                    controls=achievement_cards,
                    alignment=MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


class TopView(Column):
    def __init__(self, page: Page):
        super().__init__(
            spacing=100,
            expand=True,
            scroll=ScrollMode.AUTO,
        )
        self.hero_section = create_hero_section(page, self.scroll_to_step_section)
        self.feature_section = create_feature_section()
        self.usage_section = create_usage_section()
        self.step_section = create_step_section()
        self.achievement_section = create_achievement_section()
        self.controls = [
            self.hero_section,
            self.feature_section,
            self.usage_section,
            self.step_section,
            self.achievement_section,
        ]

    def scroll_to_step_section(self, _):
        self.scroll_to(key="step_section", duration=500)
        self.update()


if __name__ == "__main__":

    def main(page: Page) -> None:
        page.title = "test app"
        page.scroll = "auto"
        example = TopView(page)
        page.add(example)

    app(main)
