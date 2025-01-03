import logging
import os

import flet as ft

logger = logging.getLogger(__name__)



async def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.appbar = ft.AppBar(title=ft.Text("Audio Recorder"), center_title=True)

    path = f"{os.environ["FLET_APP_STORAGE_TEMP"]}/test_audio.wav"

    # 録音開始ハンドラ
    async def handle_start_recording(e):
        if not await audio_rec.has_permission_async():
            logger.error("No Permission")
            return
        devices = await audio_rec.get_input_devices_async()
        if not devices:
            logger.error("No Devices")
            return
        logger.debug(f"StartRecording: {path}")
        audio_rec.start_recording(path)

    # 録音停止ハンドラ
    async def handle_stop_recording(e):
        output_path = audio_rec.stop_recording()
        logger.debug(f"StopRecording: {output_path}")
        if page.web and output_path is not None:
            page.launch_url(output_path)

    # デバイスリスト取得ハンドラ
    async def handle_list_devices(e):
        devices = await audio_rec.get_input_devices_async()
        logger.debug(devices)

    # パーミッション確認ハンドラ
    async def handle_has_permission(e):
        try:
            logger.debug(f"HasPermission: {await audio_rec.has_permission_async()}")
        except Exception as err:
            print(err)

    # 録音一時停止ハンドラ
    async def handle_pause(e):
        is_recording = await audio_rec.is_recording_async()
        logger.debug(f"isRecording: {is_recording}")
        if is_recording:
            audio_rec.pause_recording()

    # 録音再開ハンドラ
    async def handle_resume(e):
        is_paused = await audio_rec.is_paused_async()
        logger.debug(f"isPaused: {is_paused}")
        if is_paused:
            audio_rec.resume_recording()

    # サポートされているエンコーダのテスト
    async def handle_audio_encoding_test(e):
        for i in list(ft.AudioEncoder):
            logger.debug(f"{i}: {await audio_rec.is_supported_encoder_async(i)}")

    async def handle_state_change(e):
        logger.debug(f"State Changed: {e.data}")

    audio_rec = ft.AudioRecorder(
        audio_encoder=ft.AudioEncoder.WAV,
        on_state_changed=handle_state_change,
    )
    page.overlay.append(audio_rec)
    page.update()

    page.add(
        ft.ElevatedButton("Start Audio Recorder", on_click=handle_start_recording),
        ft.ElevatedButton("Stop Audio Recorder", on_click=handle_stop_recording),
        ft.ElevatedButton("List Devices", on_click=handle_list_devices),
        ft.ElevatedButton("Pause Recording", on_click=handle_pause),
        ft.ElevatedButton("Resume Recording", on_click=handle_resume),
        ft.ElevatedButton("Test AudioEncodings", on_click=handle_audio_encoding_test),
        ft.ElevatedButton("Has Permission", on_click=handle_has_permission),
    )



if __name__ == "__main__":
    from app.logging_config import setup_logging
    setup_logging()
    ft.app(main)
