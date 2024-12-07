import os
import sqlite3
from collections.abc import Iterator
from typing import Annotated, Any

from IPython.display import Image, display
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from psycopg_pool import ConnectionPool
from typing_extensions import TypedDict

from app.ai.settings import langsmith_settigns, llm_settings
from app.ai.tools import DisplayOperationTool, tools
from app.settings import load_settings
from app.unity_conn import SocketServer


class State(TypedDict):
    messages: Annotated[list, add_messages]


class ChatbotGraph:
    def __init__(self, server: SocketServer, verbose: bool = False):
        self.graph_builder = StateGraph(State)
        langsmith_settigns()
        try:
            self.llm = llm_settings(verbose=verbose)
            self.tools = tools
            self.tools.append(DisplayOperationTool(server=server))
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            self._initialize_memory()
            self._initialize_graph()
        except ValueError as e:
            print(e)
            raise ValueError("AIの初期化に失敗しました。\nLLMとDatabaseの設定を見直してください。") from e
        except Exception as e:
            raise e

    def _initialize_graph(self) -> None:
        self.graph_builder.add_node("chatbot", self.chatbot)
        tool_node = ToolNode(tools=tools)
        self.graph_builder.add_node("tools", tool_node)
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.set_entry_point("chatbot")

        self.graph = self.graph_builder.compile(checkpointer=self.memory)

    def _initialize_memory(self) -> None:
        settings = load_settings("db_settings")
        if settings["use_postgres"]:
            self.DB_URI = "postgresql://postgres:postgres@postgres:5432/main_db?sslmode=disable"
            self.connection_kwargs = {"autocommit": True, "prepare_threshold": 0}
            self.pool = ConnectionPool(conninfo=self.DB_URI, max_size=20, kwargs=self.connection_kwargs, open=True)
            self.memory = PostgresSaver(self.pool)
            self.memory.setup()
        else:
            self.memory = SqliteSaver(sqlite3.connect("chat_memory.db", check_same_thread=False))

    def set_memory_config(self, thread_id: str) -> RunnableConfig:
        self.memory_config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        return self.memory_config

    def chatbot(self, state: State) -> dict:
        return {"messages": [self.llm_with_tools.invoke(state["messages"])]}

    def draw_graph(self, output_file: str | None = None) -> None:
        try:
            if output_file is None:
                this_dir = os.path.dirname(os.path.abspath(__file__))
                output_file = f"{this_dir}/graph.png"
            display(Image(self.graph.get_graph().draw_mermaid_png(output_file_path=output_file)))
        except Exception as e:
            raise ValueError("グラフの描画に失敗しました。") from e

    def stream_graph_updates(self, user_input: str, config: RunnableConfig | None = None) -> Iterator[Any]:
        if config is None:
            self.set_memory_config("1")

        try:
            events = self.graph.stream({"messages": [("user", user_input)]}, self.memory_config, stream_mode="values")
            for event in events:
                yield event["messages"][-1]
        except Exception as e:
            raise ValueError("ストリーム更新に失敗しました。") from e





if __name__ == "__main__":
    import pprint
    from threading import Thread

    from app.unity_conn import SocketServer

    server = SocketServer()
    server_thread = Thread(target=server.start, daemon=True)
    server_thread.start()

    chatbot_graph = ChatbotGraph(verbose=True, server=server)

    chatbot_graph.draw_graph()

    config = {"configurable": {"thread_id": "1"}}
    chat_history = chatbot_graph.graph.get_state(config)
    messages_list = chat_history.values["messages"]
    pprint.pprint(messages_list)
    for i, message in enumerate(messages_list, start=1):
        sender = "ユーザー" if "HumanMessage" in str(type(message)) else "アシスタント"
        print(f"{i}. **{sender}:** {message.content}")



    # while True:
    #     try:
    #         user_input = input("User: ")
    #         if user_input.lower() in ["quit", "exit", "q"]:
    #             print("Goodbye!")
    #             break

    #         for response in chatbot_graph.stream_graph_updates(user_input):
    #             print("Assistant:", response.pretty_print())
    #     except Exception as e:
    #         raise ValueError("ストリーム更新に失敗しました。") from e
