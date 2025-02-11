import logging
import os
import sqlite3
from typing import Annotated, Literal

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

# from IPython.display import Image, display
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, tool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from app.ai.settings import llm_settings
from app.ai.vector_db import get_vector_store
from app.controller.manager.settings_manager import SettingsManager
from app.models.agent_models import State

logger = logging.getLogger(__name__)


# -----------------------------
# ツールの定義
# -----------------------------
class SubAgent:
    """
    サブエージェントを表すクラス
    このクラスは、エージェントの設定情報とツールのリストを受け取り、
    エージェントを生成する。

    Args:
        llm: LLM の設定情報
        tools: 使用するツールのリスト
        prompt: エージェントのプロンプト
        name: エージェントの名前
        description: エージェントの説明

    Example:
        ```python
        sub_agent= SubAgent(
        llm=llm,
        tools=[display_info_tool, document_search_tool],
        prompt="Please provide the information",
        name="SubAgent1",
        description="This is a sub-agent for information retrieval.",
        )
        sub_agent.invoke(state)
        sub_agent.node(state)
        ```
    """

    def __init__(self, tools, prompt: str, name: str, description: str):
        self.tools = tools
        self.prompt = prompt
        self.name = name
        self.description = description
        self.llm = llm_settings(tags=[self.name])
        self.agent = self.initialize_agent(tools=self.tools)

    def initialize_agent(self, tools = None):
        return create_react_agent(self.llm, tools=tools, prompt=self.prompt, name=self.name)

    def get_full_prompts(self):
        return self.agent.get_prompts()

    def invoke(self, state):
        return self.agent.invoke(state)

    def node(self, state):
        result = self.invoke(state)
        return Command(
            update={"messages": [AIMessage(content=result["messages"][-1].content, name=self.name)]},
            goto="supervisor",
        )

    def rebind_tools(self, tools):
        self.agent = self.initialize_agent(tools=tools)


# displayを扱うSubAgent ------------------------------------
# @tool
# def display_info_tool() -> str:
#     """
#     現在ディスプレイに表示されている3Dモデルの情報を返す関数
#     """
#     # TODO:ディスプレイに表示されている3Dモデルの情報を返す処理を追加する
#     logger.debug("\n\ndisplay_info_tool called\n\n")
#     current_display_object = {"id": "ABC123", "title": "NAO"}
#     return (
#         "現在のディスプレイオブジェクト: "
#         f"3Dモデル ID: {current_display_object['id']}, タイトル: '{current_display_object['title']}'"
#     )

class DisplayInfoTool(BaseTool):
    """
    現在ディスプレイに表示されている3Dモデルの情報を返すツール
    """
    name: str = "display_info_tool"
    description: str = "現在ディスプレイに表示されている3Dモデルの情報を返すツール"

    dammy_model: str = "dammy"

    def _run(self, run_manager: CallbackManagerForToolRun | None = None) -> str:
        """
        現在ディスプレイに表示されている3Dモデルの情報を返す関数
        """
        # TODO:ディスプレイに表示されている3Dモデルの情報を返す処理を追加する
        logger.debug("\n\ndisplay_info_tool called\n\n")
        return f"現在のディスプレイオブジェクト: 3Dモデル ID: ABC123, タイトル: '{self.dammy_model}'"

    def _arun(self, run_manager: AsyncCallbackManagerForToolRun | None = None) -> str:
        return self._run(run_manager=run_manager.get_sync())


# def model_change_tool(model_name: Annotated[str, "変更したいモデルの名前"]) -> str:
#     """
#     モデルを変更する関数
#     model_nameに基づいて、モデルを変更する
#     もしmodel_nameがわからなければユーザーにたずねる必要がある
#     """
#     # TODO:モデルを変更する処理を追加する
#     logger.debug(f"\n\nmodel_change_tool called with model_name={model_name}\n\n")
#     return f"モデルを{model_name}に変更しました。"

class ModelChangeInput(BaseModel):
    model_name: str = Field(description="変更したいモデルの名前")

class ModelChangeTool(BaseTool):
    """
    モデルを変更するツール
    """
    name: str = "model_change_tool"
    description: str = "モデルを変更するツール"
    args_schema: type[BaseModel] = ModelChangeInput

    def _run(self, model_name: str, run_manager: CallbackManagerForToolRun | None = None) -> str:
        """
        モデルを変更する関数
        model_nameに基づいて、モデルを変更する
        もしmodel_nameがわからなければユーザーにたずねる必要がある
        """
        # TODO:モデルを変更する処理を追加する
        logger.debug(f"\n\nmodel_change_tool called with model_name={model_name}\n\n")
        return f"モデルを{model_name}に変更しました。"

    def _arun(self, model_name: str, run_manager: AsyncCallbackManagerForToolRun | None = None) -> str:
        return self._run(model_name, run_manager=run_manager.get_sync())


display_agent_prompt = """
あなたはディスプレイ全般を扱うエージェントです。
あなたは与えられたtoolを使って、ユーザーの要求にこたえることができます。

# あなたに与えられた役割
- ディスプレイ情報を提供する
- ディスプレイの制御を行う
- 変更した内容や取得して情報をユーザーにわかりやすいようにまとめて返す
"""
display_agent_description = """
ディスプレイ全般を扱うエージェントです。
このエージェントは、ディスプレイ情報の提供やディスプレイの制御を行います。
ディスプレイに関することやモニター、SRD(ディスプレイの名前)に関することはこのエージェントが適切です。
"""
display_agent = SubAgent(
    tools=[],
    prompt=display_agent_prompt,
    name="DisplayControlAgent",
    description=display_agent_description,
)


# documentを扱うSubAgent ------------------------------------
@tool
def document_search_tool(query: Annotated[str, "The query to search documents for."]) -> str:
    """
    ドキュメントを検索する関数
    queryに基づいて、3Dモデル解説ドキュメントを検索し、類似度の高いドキュメントを返す
    """
    logger.debug(f"document_search_tool called with query={query}")
    try:
        res = get_vector_store().similarity_search(query=query)
        if not res:
            return "類似ドキュメントは見つかりませんでした。"
        logger.debug(f"document_search_tool result: {res}")
        return res
    except Exception as e:
        logger.error(e)
        return f"ドキュメントの検索に失敗しました。{e}"


document_agent_prompt = """
あなたはドキュメント全般を扱うエージェントです。
あなたは与えられたtoolを使って、ユーザーの要求にこたえることができます。

# あなたに与えられた役割
- ドキュメントの検索を行う
- ドキュメントの要約を行う
- 要約する際はMarkdown形式で返すこと
- ユーザーにわかりやすく丁寧な説明を行い、特に指示がない場合は簡潔にまとめること
- 参考にしたドキュメントを返す場合は"[参考にしたドキュメント](metadataのsourceに格納されている数値)"のような形で返すこと

# 注意
基本的には検索をおこなってそれをまとめるのがあなたの役割ですが、検索結果が見つからなかった場合やエラーが発生した場合は、その旨をユーザーに伝えてください。
また、検索結果がユーザーが求めているものと異なる場合は、その旨をユーザーに伝えて、再度検索を行うかどうかを確認してください。
嘘をついたり、不適切な情報を提供することは厳禁です。
できるだけ正確な情報を提供するように心がけてください。
"""
document_agent_description = """
3Dモデルのドキュメント全般を扱うエージェントです。
このエージェントは、ドキュメントの検索や要約を行います。
ドキュメントに関することや解説、要約に関することはこのエージェントが適切です。
説明を求められたり、「教えて」や「解説して」などの要求があった場合はこのエージェントを選択してください。
"""
document_agent = SubAgent(
    tools=[document_search_tool],
    prompt=document_agent_prompt,
    name="DocumentSearchAgent",
    description=document_agent_description,
)

sub_agents = [display_agent, document_agent]
sub_agents_description_prompt = "\n".join([f"{agent.name}: {agent.description}" for agent in sub_agents])

# genericを扱うSubAgent ------------------------------------
generic_agent_prompt = """
あなたは汎用エージェントです。
あなたは与えられたtoolを使って、ユーザーの要求にこたえることができます。

# あなたに与えられた役割
- ユーザーを楽しませるための雑談を行う
- ほかのエージェントが担当している内容をユーザーに提供する
- その他の雑用を行う

## 他のエージェントが担当している内容
{sub_agents_description_prompt}
"""
generic_agent_description = """
汎用エージェントです。
このエージェントは、ユーザーの要求に対して雑談や他のエージェントが担当している内容を提供します。
"""
generic_agent = SubAgent(
    tools=[],
    prompt=generic_agent_prompt,
    name="GenericAgent",
    description=generic_agent_description,
)


# 今までの履歴をまとめるエージェント ------------------------------------
summarize_agent_prompt = """
あなたは会話のまとめを行うエージェントです。
あなたは与えられたtoolを使って、ユーザーの要求に応じて会話のまとめを行うことができます。

# あなたに与えられた役割
- 会話のまとめを行う
- 会話の流れを把握し、ユーザーに対して必要な情報のみを提供する
"""


sub_agents_with_generic = sub_agents + [generic_agent]
sub_agents_with_generic_description_prompt = "\n".join(
    [f"{agent.name}: {agent.description}" for agent in sub_agents_with_generic]
)




# -----------------------------
# スーパーバイザーの定義
# -----------------------------
members = [agent.name for agent in sub_agents_with_generic]
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*options]  # type: ignore


system_prompt = f"""
あなたは以下のワーカー間の会話を管理するように指示されたスーパーバイザーです:
{sub_agents_with_generic_description_prompt}

# あなたがするべきこと
次のユーザー要求に対して、次にアクションを起こすワーカーを指定してください。
各ワーカーはタスクを実行し、その結果とステータスを返信します。
適切なワーカーがいない場合はGenericAgentを選択してください。
終了したら、FINISH で応答してください。

# 例
以下のような例を参考にしてユーザーと会話してください。
この例は複数回のやり取りを想定しているものもあります。

- 例1:
    - ユーザー: "今映っている奴について教えて"
    - あなた: DisplayControlAgent
    - DisplayControlAgent: "現在のディスプレイオブジェクト: 3Dモデル ID: ABC123, タイトル: 'NAO'"
    - 次のアクション: FINISH
- 例2:
    - ユーザー: "今表示されているモデルの解説を教えて"
    - あなた: DisplayControlAgent
    - DisplayControlAgent: "現在のディスプレイオブジェクト: 3Dモデル ID: ABC123, タイトル: 'NAO'"
    - あなた: DocumentSearchAgent
    - DocumentSearchAgent: "NAOの解説は以下の通りです: ..."
    - あなた: FINISH
- 例3:
    - ユーザー: "モデルを変更して"
    - あなた: DisplayControlAgent
    - DisplayControlAgent: "どんなモデルに変更しますか？"
    - あなた: FINISH
    - ユーザーから再度の入力: "NAOに変更して"
    - あなた: DisplayControlAgent
    - DisplayControlAgent: "モデルをNAOに変更しました。"
    - あなた: FINISH

# 注意
あなたはワーカーの指示を行うだけで、ユーザーとの直接のやり取りは行いません。
同じワーカーを何度も指定しないでください。
完璧を求めず、適切なワーカーを指定してください。
"""


class SupervisorAgent:
    def __init__(
        self,
        sub_agents: list[SubAgent],
        settings_manager: SettingsManager,
        thread_id: str = None,
        verbose: bool = False,
    ):
        self.llm = llm_settings(tags=["supervisor"])
        self.llm.tags = ["supervisor"]
        self.sub_agents = sub_agents
        self.settings_manager = settings_manager
        self.thread_id = thread_id
        self.verbose = verbose

        self._initialize_memory()
        self.graph = self._initialize_graph()

    def _initialize_memory(self):
        db_settings = self.settings_manager.load_settings().database_settings
        if db_settings.use_postgres:
            postgres_settings = db_settings.postgres_settings
            self.DB_URI = f"postgresql://{postgres_settings.user}:{postgres_settings.password}@{postgres_settings.host}:{postgres_settings.port}/{postgres_settings.database}?sslmode=disable"
            self.connection_kwargs = {"autocommit": True, "prepare_threshold": 0}
            self.pool = ConnectionPool(conninfo=self.DB_URI, max_size=20, kwargs=self.connection_kwargs, open=True)
            self.memory = PostgresSaver(self.pool)
            self.memory.setup()
        else:
            self.memory = SqliteSaver(sqlite3.connect("chat_memory.db", check_same_thread=False))

    def _initialize_graph(self):
        builder = StateGraph(State)
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", self.node)
        for agent in self.sub_agents:
            builder.add_node(agent.name, agent.node)
        graph = builder.compile(checkpointer=self.memory)
        return graph

    @property
    def memory_config(self):
        return {"configurable": {"thread_id": self.thread_id}}

    def draw_graph(self, output_file: str | None = None) -> None:
        try:
            if output_file is None:
                this_dir = os.path.dirname(os.path.abspath(__file__))
                output_file = f"{this_dir}/graph.png"
            display(Image(self.graph.get_graph().draw_mermaid_png(output_file_path=output_file)))
        except Exception as e:
            raise ValueError("グラフの描画に失敗しました。") from e

    def node(self, state: State) -> Command[Literal[*members, "__end__"]]:  # type: ignore
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = self.llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            logger.debug("Finished conversation")
            goto = END

        return Command(goto=goto, update={"next": goto})

    def stream(self, user_message: str, thread_id: str = None, debug: bool = False):
        if not thread_id and not self.thread_id:
            raise ValueError("thread_id is required.")
        if thread_id:
            self.thread_id = thread_id

        send_message = {"messages": [("user", user_message)]}
        stream_mode = ["messages"] if not debug else ["updates", "messages"]

        try:
            # ここでLLMによる応答を生成、ストリーミングで返す
            if debug:
                yield from self.graph.stream(send_message, config=self.memory_config, stream_mode=stream_mode)
            else:
                for _, message in self.graph.stream(send_message, config=self.memory_config, stream_mode=stream_mode):
                    yield message

            # yield from self.graph.stream(
            #     send_message,
            # subgraphs=True,
            #     config=self.memory_config,
            #     stream_mode=["messages"],
            # )
            print("===" * 20 + " FINISH " + "===" * 20)
        except Exception as e:
            logger.error(e)
            raise ValueError("ストリーム更新に失敗しました。") from e


if __name__ == "__main__":
    from app.logging_config import setup_logging

    setup_logging()

    thread_id = "test_thread_id4"
    settings_manager = SettingsManager()
    supervisor = SupervisorAgent(sub_agents_with_generic, settings_manager=settings_manager, thread_id=thread_id)
    display_agent.rebind_tools([DisplayInfoTool(), ModelChangeTool()])
    print("----" * 30 + "\n")
    for res, metadata in supervisor.stream("今映っている奴について教えて", debug=True):
        # print(res)
        if res.content and any(agent.name in metadata.get("tags", []) for agent in sub_agents_with_generic):
            print(res.content, end="", flush=True)
