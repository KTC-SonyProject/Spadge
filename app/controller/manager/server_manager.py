import json
import logging
import socket

from app.logging_config import safe_log
from app.models.command_models import CommandBase, TransferCommand

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
        self.running = False
        self.is_connected = False

    def start(self) -> None:
        """
        サーバを起動
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(1)
            logger.info(f"サーバーが起動しました: {self.host}:{self.port}")
            self.running = True
        except OSError as e:
            logger.error(f"サーバを起動させるポートがすでに使用されています: {e}")
            self.stop()
        except BaseException as e:
            logger.error(f"サーバーの起動中にエラーが発生しました: {e}")
            self.stop()

        self.wait_for_connection()



    def wait_for_connection(self) -> None:
        """
        クライアントの接続を待機
        """
        try:
            logger.info("クライアントの接続を待機中...")
            while self.running:
                if self.server_socket is None:
                    break
                try:
                    self.client_socket, self.client_address = self.server_socket.accept()
                    logger.info(f"クライアントが接続しました: {self.client_address}")
                    self.handle_client(self.client_socket)
                except TimeoutError:
                    continue
        except KeyboardInterrupt:
            logger.info("サーバーを停止します")
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
        safe_log(logger, logging.INFO, "サーバーを停止しました")

    def _wait_for_result(self) -> dict:
        logger.info("Waiting for result...")

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

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        クライアントとの通信を処理するスレッドを管理

        Args:
            client_socket (socket.socket): クライアントとの通信用ソケット
        """
        self.is_connected = True
        try:
            # クライアントからのデータを受け取る処理（必要なら実装）
            while self.is_connected:
                if not self.client_socket:
                    break
                # data = client_socket.recv(1024).decode("utf-8")
                # if not data:
                #     break
                # logger.debug(f"クライアントからのデータ: {data}")
        except Exception as e:
            logger.error(f"クライアント処理中にエラーが発生しました: {e}")
        finally:
            client_socket.close()
            self.is_connected = False
            logger.info("クライアントとの接続を終了しました")
            self.wait_for_connection()

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
