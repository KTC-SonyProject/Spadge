import os
import sqlite3
from collections.abc import Iterator
from typing import Annotated, Any
from uuid import uuid4

from IPython.display import Image, display
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from psycopg_pool import ConnectionPool
from typing_extensions import TypedDict

from app.ai.settings import embedding_model_settings, llm_settings
from app.ai.tools import tools
from app.settings import load_settings


def create_document_obj(content: str, document_id: int) -> list[Document]:
    """
    ドキュメントオブジェクトを作成する関数
    """
    document = Document(
        page_content=content,
        metadata={
            "source": document_id
        }
    )
    return [document]


def get_vector_store():
    """
    ベクトルストアを作成する関数
    """
    embeddings = embedding_model_settings()
    return Chroma(
        collection_name="document_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

def add_document_to_vectorstore(content: str, document_id: int):
    """
    ドキュメントをベクトルストアに追加する関数
    """
    documents = create_document_obj(content, document_id)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store = get_vector_store()
    vector_store.add_documents(documents=documents, ids=uuids)
    print("Document added to vector store.")



class State(TypedDict):
    messages: Annotated[list, add_messages]


class ChatbotGraph:
    def __init__(self, llm_type: str = "AzureChatOpenAI", verbose: bool = False):
        self.graph_builder = StateGraph(State)
        self.llm = llm_settings(verbose=verbose)
        self.llm_with_tools = self.llm.bind_tools(tools)
        self._initialize_memory()
        self._initialize_graph()

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
        settings = load_settings()
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

        events = self.graph.stream({"messages": [("user", user_input)]}, self.memory_config, stream_mode="values")

        for event in events:
            yield event["messages"][-1]





if __name__ == "__main__":
    # import pprint

    # chatbot_graph = ChatbotGraph(verbose=True)

    # chatbot_graph.draw_graph()

    # config = {"configurable": {"thread_id": "1"}}
    # chat_history = chatbot_graph.graph.get_state(config)
    # messages_list = chat_history.values["messages"]
    # pprint.pprint(messages_list)
    # for i, message in enumerate(messages_list, start=1):
    #     sender = "ユーザー" if "HumanMessage" in str(type(message)) else "アシスタント"
    #     print(f"{i}. **{sender}:** {message.content}")



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

    results = get_vector_store().similarity_search(
        "test",
    )
    print(results)
    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")
