from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.ai.settings import embedding_model_settings
from app.controller.manager.settings_manager import SettingsManager, load_settings
from app.models.database_models import DatabaseHandler

# from app.db_conn import DatabaseHandler


def create_document_obj(content: str, document_id: int, return_list: bool = True) -> Document | list[Document]:
    """
    ドキュメントオブジェクトを作成する関数
    """
    document = Document(page_content=content, metadata={"source": f"{document_id}"})
    if return_list:
        return [document]
    else:
        return document


def get_main_db() -> str:
    """
    メインDBを取得する関数
    """
    settings = load_settings("database_settings")
    if settings["use_postgres"]:
        return "postgresql://postgres:postgres@postgres:5432/main_db?sslmode=disable"
    else:
        return "sqlite:///indexing.db"


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


def indexing_document(content: str, document_id: int):
    """
    ドキュメントをインデックスする関数
    """
    docs = create_document_obj(content, document_id)

    vector_store = get_vector_store()
    record_manager = SQLRecordManager(
        namespace="chromadb/document_collection",
        db_url=get_main_db(),
    )
    record_manager.create_schema()
    result = index(
        docs,
        record_manager,
        vector_store,
        cleanup="incremental",
        source_id_key="source",
    )
    print(f"{result=}")
    print("Document indexed.")


def delete_document_from_vectorstore(document_id: int):
    """
    ドキュメントをベクトルストアから削除する関数
    """
    # 削除するドキュメント以外のドキュメントを取得する
    settings_manager = SettingsManager()
    db = DatabaseHandler(settings_manager)
    all_documents = db.fetch_query("SELECT * FROM documents WHERE document_id != %s", (document_id,))
    docs = []
    for doc in all_documents:
        docs.append(create_document_obj(doc[2], doc[0], return_list=False))
    vector_store = get_vector_store()
    record_manager = SQLRecordManager(
        namespace="chromadb/document_collection",
        db_url=get_main_db(),
    )
    result = index(
        docs,
        record_manager,
        vector_store,
        cleanup="full",
        source_id_key="source",
    )
    print(f"{result=}")
    print("Document deleted from vector store.")


# def add_document_to_vectorstore(content: str, document_id: int):
#     """
#     ドキュメントをベクトルストアに追加する関数
#     """
#     documents = create_document_obj(content, document_id)
#     uuids = [str(uuid4()) for _ in range(len(documents))]
#     vector_store = get_vector_store()
#     vector_store.add_documents(documents=documents, ids=uuids)
#     print("Document added to vector store.")
#     return uuids


def _clear_vectordb():
    vectorstore = get_vector_store()
    record_manager = SQLRecordManager(
        namespace="chromadb/document_collection",
        db_url=get_main_db(),
    )
    """Hacky helper method to clear content. See the `full` mode section to to understand why it works."""
    index([], record_manager, vectorstore, cleanup="full", source_id_key="source")
    print("Vector store cleared.")


if __name__ == "__main__":
    # indexing_document("Hello, world!sss", 1)
    # indexing_document("こんにちは、世界！", 2)

    # # delete_document_from_vectorstore(1)

    # results = get_vector_store().similarity_search(
    #     "test",
    # )
    # print(results)
    # for res in results:
    #     print(f"* {res.page_content} [{res.metadata}]")

    _clear_vectordb()
