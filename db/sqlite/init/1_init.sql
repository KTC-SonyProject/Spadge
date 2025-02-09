-- ドキュメントテーブル作成
DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    created_at DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP,'localtime')),
    updated_at DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP,'localtime'))
);

--オブジェクトの名前とファイル名を保存するテーブル
DROP TABLE IF EXISTS objects;
CREATE TABLE objects (
    object_id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_name TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP,'localtime')),
    updated_at DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP,'localtime'))
);
