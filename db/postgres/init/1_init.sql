-- 作成したDBに接続
\c main_db;

-- ドキュメントテーブル作成
DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
	document_id SERIAL PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	content TEXT,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--オブジェクトの名前とファイル名を保存するテーブル
DROP TABLE IF EXISTS objects;
CREATE TABLE objects (
	object_id SERIAL PRIMARY KEY,
	object_name VARCHAR(100) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	delete_flag BOOLEAN NOT NULL DEFAULT FALSE
);

-- データベースののぞき方
-- docker container exec -it spadge-main_db bash
-- psql -U postgres -d postgres