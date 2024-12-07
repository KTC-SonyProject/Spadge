import logging
import os
import socket

logger = logging.getLogger(__name__)

class SocketServer:
    """
    Socketサーバーを管理するクラス
    """
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        self.is_connected = False

    def start(self) -> None:
        """
        サーバを起動
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            logger.info(f"サーバーが起動しました: {self.host}:{self.port}")
            self.running = True
        except OSError as e:
            logger.error(f"サーバーの起動中にエラーが発生しました: {e}")
            self.stop()
        except Exception as e:
            logger.error(f"サーバーの起動中にエラーが発生しました: {e}")
            self.stop()

        try:
            while self.running:
                logger.info("クライアントの接続を待機中...")
                self.client_socket, self.client_address = self.server_socket.accept()
                logger.info(f"クライアントが接続しました: {self.client_address}")
                self.handle_client(self.client_socket)
        except KeyboardInterrupt:
            logger.info("サーバーを停止します")
        except Exception as e:
            logger.error(f"サーバーでエラーが発生しました {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """
        サーバーを停止
        """
        self.running = False
        self.is_connected = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        logger.info("サーバーを完全に停止しました")

    def _wait_for_result(self) -> str:
        """
        クライアントからRESULT行を受け取るまでブロッキングで待機するユーティリティ
        """
        buffer = ""
        while True:
            data = self.client_socket.recv(1024).decode('utf-8')
            if not data:
                raise ConnectionError("クライアントとの接続が切断されました")
            buffer += data
            lines = buffer.split('\n')
            # 最後の行は未完成の可能性があるので、完全な行だけ処理
            for i in range(len(lines)-1):
                line = lines[i].strip()
                if line.startswith("RESULT:"):
                    # 結果を返す
                    return line[len("RESULT:"):]
            # 未完成の最後の行をbufferに残す
            if not buffer.endswith('\n'):
                buffer = lines[-1]
            else:
                buffer = ""

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        クライアントとの通信を処理するスレッドを管理

        Args:
            client_socket (socket.socket): クライアントとの通信用ソケット
        """
        self.is_connected = True
        try:
            # クライアントからのデータを受け取る処理（必要なら実装）
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                logger.debug(f"クライアントからのデータ: {data}")
        except Exception as e:
            logger.error(f"クライアント処理中にエラーが発生しました: {e}")
        finally:
            client_socket.close()
            self.is_connected = False
            logger.info("クライアントとの接続を終了しました")

    def send_command(self, command: str) -> str:
        """
        クライアントにコマンドを送信

        Args:
            command (str): 送信するコマンド
        """
        if self.client_socket:
            try:
                message = f"COMMAND:{command}\n"
                self.client_socket.sendall(message.encode('utf-8'))
                logger.debug(f"コマンドを送信しました: {command}")

                # コマンドの実行結果を待機
                result = self._wait_for_result()
                logger.info(f"コマンドの実行結果: {result}")
                return result
            except Exception as e:
                logger.error(f"コマンド送信中にエラーが発生しました: {e}")
        else:
            logger.warning("クライアントが接続されていません")

    def send_file(self, file_path: str) -> str:
        """
        クライアントにファイルを送信

        Args:
            file_path (str): 送信するファイルのパス

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            e: その他のエラー
        """
        if self.client_socket:
            try:
                if not os.path.isfile(file_path):
                    logger.error(f"ファイルが見つかりません: {file_path}")
                    raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

                # ファイル情報を送信
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_header = f"FILE:{file_name}:{file_size}\n"
                self.client_socket.sendall(file_header.encode('utf-8'))

                # ファイル内容を送信
                with open(file_path, "rb") as f:
                    while chunk := f.read(1024):
                        self.client_socket.sendall(chunk)

                logger.debug(f"ファイルを送信しました: {file_path}")

                # ファイルの送信結果を待機
                result = self._wait_for_result()
                logger.info(f"ファイルの送信結果: {result}")
                return result
            except Exception as e:
                raise e
        else:
            logger.warning("クライアントが接続されていません")
