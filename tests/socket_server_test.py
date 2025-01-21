import logging
from queue import Empty, Queue
from threading import Thread
from time import sleep

from app.controller.manager.server_manager import ServerManager
from app.models.command_models import (
    ControlCommand,
    ListCommand,
    NextCommand,
    PingCommand,
    PreviousCommand,
    TransferCommand,
)

logging.basicConfig(level=logging.DEBUG)

server = ServerManager()
server_thread = Thread(target=server.start, daemon=True)
server_thread.start()

print("クライアントの接続を待機中...")


input_queue = Queue()


def input_thread(queue):
    """ユーザー入力を非同期にキューに追加するスレッド"""
    while True:
        user_input = input()  # ブロッキングな入力
        queue.put(user_input)  # 入力をキューに送る


Thread(target=input_thread, args=(input_queue,), daemon=True).start()


def get_input(question_print: str = "選択してください"):
    print(f"{question_print}: ", end="", flush=True)
    while server.is_connected:
        try:
            option = input_queue.get(timeout=1)  # 1秒間待機
        except Empty:
            continue

        if not isinstance(option, str):
            raise ValueError("無効な入力です。")
            break
        else:
            return option


# コマンドの種類を選ぶメニューを表示
def display_menu():
    print("\n\n送信オプション: ")
    print("----------------")
    print("1: controlコマンドを送信")
    print("2: transferコマンドを送信")
    print("3: nextコマンドを送信")
    print("4: previousコマンドを送信")
    print("5: listコマンドを送信")
    print("6: pingコマンドを送信")
    print("q: サーバーを停止")
    print("----------------")


def choose_command(command_num: str):
    match command_num:
        case "1":
            action = get_input("アクション内容を入力してください")
            command_obj = ControlCommand(object_id="1", action=action, action_parameters={"param1": "value1"})
        case "2":
            file_path = get_input("ファイルのパスを入力してください")
            try:
                command_obj = TransferCommand(file_path)
            except FileNotFoundError as e:
                print(f"ファイルが見つかりません: {e}")
                return
        case "3":
            command_obj = NextCommand()
        case "4":
            command_obj = PreviousCommand()
        case "5":
            command_obj = ListCommand()
        case "6":
            command_obj = PingCommand()
        case "q":  # サーバーを停止
            server.stop()
            return
        case _:
            print("無効な選択です。もう一度試してください")
            return

    server.send_command(command_obj)


def main():
    last_connection_state = server.is_connected  # 接続状態を記録

    try:
        while True:
            # 接続状態が変化した場合のみメッセージを表示
            if server.is_connected != last_connection_state:
                last_connection_state = server.is_connected
                if not server.is_connected:
                    print("クライアントとの接続がありません。再接続を待機しています...")
                else:
                    print("クライアントに接続されました。")

            # サーバーが接続されていない場合は再接続を待機
            if not server.is_connected:
                sleep(1)
                continue

            display_menu()
            option = get_input()
            choose_command(option)
    except KeyboardInterrupt:
        print("\nサーバーを停止します")
        server.stop()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        server.stop()


if __name__ == "__main__":
    main()
