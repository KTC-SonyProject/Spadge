from enum import Enum

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.documents import Document
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from app.ai.vector_db import get_vector_store
from app.unity_conn import SocketServer


class SearchDocumentInput(BaseModel):
    query: str = Field(description="ドキュメントを検索するクエリ")

@tool("search_documents_tool", args_schema=SearchDocumentInput)
def search_documents_tool(query: str) -> list[Document]:
    """
    ドキュメントを検索する関数
    この関数で取得したドキュメントをユーザーに返す場合は"[参考にしたドキュメント](metadataのsourceに格納されている数値)"のような形で返す
    """
    results = get_vector_store().similarity_search(
        query=query,
    )
    # results = {
    #     "content": res["content"],
    # }
    return results

class OperationCommand(Enum):
    next_scene = "次のシーン"
    previous_scene = "前のシーン"
    rotate_scene = "シーンを回転"


class DisplayOperationInput(BaseModel):
    operation: str = Field(
        description=(
            f"操作内容 操作は以下のいずれかの文字列で指定する: {', '.join([op.value for op in OperationCommand])}"
        )
    )


class DisplayOperationTool(BaseTool):
    name: str = "display_operation_tool"
    description: str = "Displayの操作を行う"
    args_schema: type[BaseModel] = DisplayOperationInput

    server: SocketServer

    def send_command(self, command: str) -> None:
        """
        クライアントにコマンドを送信

        Args:
            command (str): 送信するコマンド
        """
        try:
            self.server.send_command(command)
        except Exception as e:
            raise e

    def _run(self, operation: str, run_manager: CallbackManagerForToolRun | None = None) -> str:
        """
        Displayの操作を行う関数

        Args:
            operation (str): 操作内容
            run_manager (CallbackManagerForToolRun | None): Callback manager for tool run. Defaults to None.

        Returns:
            str: 操作結果
        """
        if OperationCommand.next_scene.value == operation:
            # 次のシーンを表示する
            self.send_command("next")
        elif OperationCommand.previous_scene.value == operation:
            # 前のシーンを表示する
            self.send_command("previous")
        elif OperationCommand.rotate_scene.value == operation:
            # シーンを回転する
            self.send_command("rotate")
        else:
            raise ValueError(f"Invalid operation: {operation}")

        return f"次の操作を行いました: {operation}"

    async def _arun(
        self,
        operation: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        """
        Displayの操作を行う関数

        Args:
            operation (str): 操作内容
            run_manager (AsyncCallbackManagerForToolRun | None): Callback manager for tool run. Defaults to None.

        Returns:
            str: 操作結果
        """
        return self._run(operation, run_manager=run_manager.get_sync())


tools = [search_documents_tool]

if __name__ == "__main__":
    print(f"{search_documents_tool.name=}, {search_documents_tool.description=}, {search_documents_tool.args=}")

    server=SocketServer()
    display_operation_tool = DisplayOperationTool(server=server.start())
    print(f"{display_operation_tool.name=}, {display_operation_tool.description=}, {display_operation_tool.args=}")


    # print(search_documents_tool.invoke("test"))
    print(display_operation_tool.invoke("次のシーン"))
