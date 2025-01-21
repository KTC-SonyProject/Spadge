import json
import logging
import socket
import threading
import time

from app.models.command_models import CommandBase, PingCommand, TransferCommand

logger = logging.getLogger(__name__)


class ServerManager:
    """
    Socketサーバーを管理するクラス
    """

    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.thread = None
        self.running = False
        self.is_connected = False

    def start(self) -> None:
        """
        サーバを起動
        """
        try:
            logger.info(f"Starting server: {self.host}:{self.port}")
            self.running = True
            self.server_socket = self._create_server_socket()
            self.thread = threading.Thread(target=self.wait_for_connection, daemon=True)
            self.thread.start()
        except OSError as e:
            logger.error(f"サーバを起動させるポートがすでに使用されています: {e}")
            self.stop()
        except BaseException as e:
            logger.error(f"サーバーの起動中にエラーが発生しました: {e}")
            self.stop()

    def _create_server_socket(self) -> socket.socket:
        """
        サーバーソケットを作成
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        server_socket.settimeout(1)
        return server_socket

    def wait_for_connection(self) -> None:
        """
        クライアントの接続を待機
        """
        try:
            logger.info("クライアントの接続を待機中...")
            while self.running:
                # time.sleep(0.1)
                if self.server_socket is None:
                    break
                try:
                    self.client_socket, self.client_address = self.server_socket.accept()
                    logger.info(f"クライアントが接続しました: {self.client_address}")
                    self.handle_client(self.client_socket)
                except TimeoutError:
                    continue
        except OSError as e:
            if self.running:
                logger.error(f"サーバーでエラーが発生しました {e} (type: {type(e)})")
        except BaseException as e:
            logger.error(f"サーバーでエラーが発生しました {e} (type: {type(e)})")
        finally:
            self.stop()

    def stop(self) -> None:
        """
        サーバーを停止
        """
        self.running = False
        self.is_connected = False
        if self.client_socket:
            try:
                self.client_socket.sendall(b"quit\n".encode("utf-8"))
            except Exception as e:
                logger.warning(f"クライアントに終了メッセージを送信中にエラーが発生しました: {e}")
            finally:
                self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        if self.thread and self.thread.is_alive():
            try:
                # if self.thread != threading.current_thread():
                self.thread.join(timeout=3)
            except RuntimeError as _:
                pass

    def _wait_for_result(self) -> dict:
        logger.debug("Waiting for result...")

        data = self.client_socket.recv(1024).decode("utf-8")
        response = data.split("\n")
        header = response[0]
        body = response[1]
        # ボディの文字列を辞書型に変換
        try:
            body_dict = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"ボディの文字列を辞書型に変換中にエラーが発生しました: {e}")
            body_dict = {"status_message": "ERROR", "error_message": str(e)}

        logger.debug(f"受信したレスポンス: ヘッダー={header}, ボディ={body_dict}")
        return body_dict

    def _check_connection(self) -> bool:
        try:
            command = PingCommand()
            result = self.send_command(command)
            if result["status_message"] == "OK":
                return True
            else:
                logger.warning(f"接続確認に失敗しました: {result}")
                return False
        except Exception as e:
            logger.error(f"接続確認中にエラーが発生しました: {e}")
            return False

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        クライアントとの通信を処理するスレッドを管理

        Args:
            client_socket (socket.socket): クライアントとの通信用ソケット
        """
        self.is_connected = True
        try:
            while self.is_connected:
                if not self._check_connection():
                    break
                time.sleep(60)
        except Exception as e:
            logger.error(f"クライアント処理中にエラーが発生しました: {e}")
        finally:
            client_socket.close()
            self.is_connected = False
            logger.info("クライアントとの接続を終了しました")

    def _send_command(self, command: CommandBase) -> dict:
        if self.client_socket:
            try:
                full_message = command.get_command()
                self.client_socket.sendall(full_message.encode("utf-8"))

                result = self._wait_for_result()
                return result
            except Exception as e:
                logger.error(f"コマンド送信中にエラーが発生しました: {e}")
                raise e
        else:
            logger.warning("クライアントが接続されていません")
            return {"status_message": "ERROR", "error_message": "クライアントが接続されていません"}

    def send_command(self, command: CommandBase) -> dict:
        """
        クライアントにコマンドを送信

        Args:
            command (CommandBase): 送信するコマンドのインスタンス
        """
        if isinstance(command, TransferCommand):
            return self.send_file(command)

        return self._send_command(command)

    def send_file(self, command: TransferCommand) -> dict:
        """
        クライアントにファイルを送信

        Args:
            file_path (str): 送信するファイルのパス

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            e: その他のエラー
        """
        result = self._send_command(command)

        if result["status_message"] != "OK":
            logger.error(f"ファイル情報の送信に失敗しました: {result}")
            raise Exception(f"ファイル情報の送信に失敗しました: {result}")

        with open(command.file_path, "rb") as f:
            while chunk := f.read(1024):
                self.client_socket.sendall(chunk)

        logger.debug(f"ファイルを送信しました: {command.file_path}")

        result = self._wait_for_result()
        logger.info(f"ファイルの送信結果: {result}")
        return result
