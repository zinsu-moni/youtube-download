from __future__ import annotations

import os
import tempfile
from pathlib import Path

import gradio as gr
from yt_dlp import YoutubeDL


def _download(url: str, mode: str) -> tuple[str, str | None]:
    if not url or not url.strip():
        return "Please paste a YouTube URL.", None

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_template = str(Path(temp_dir) / "%(title)s.%(ext)s")

            ydl_opts: dict = {
                "outtmpl": output_template,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }

            if mode == "Audio (MP3)":
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
            elif mode == "Video 1080p (if available)":
                ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
                ydl_opts["merge_output_format"] = "mp4"
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"
                ydl_opts["merge_output_format"] = "mp4"

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url.strip(), download=True)
                title = info.get("title", "download")

                guessed_path = Path(ydl.prepare_filename(info))
                candidates = [
                    guessed_path,
                    guessed_path.with_suffix(".mp4"),
                    guessed_path.with_suffix(".mkv"),
                    guessed_path.with_suffix(".webm"),
                    guessed_path.with_suffix(".mp3"),
                    guessed_path.with_suffix(".m4a"),
                ]

                final_file = next((path for path in candidates if path.exists()), None)
                if not final_file:
                    files = sorted(Path(temp_dir).glob("*"), key=lambda x: x.stat().st_mtime)
                    final_file = files[-1] if files else None

                if not final_file:
                    return "Download finished but file could not be located.", None

                persistent_file = Path(tempfile.gettempdir()) / final_file.name
                persistent_file.write_bytes(final_file.read_bytes())

                return f"Done: {title}", str(persistent_file)

    except Exception as exc:  # noqa: BLE001
        return f"Failed: {exc}", None


with gr.Blocks(theme=gr.themes.Soft(), title="YouTube Downloader") as demo:
    gr.Markdown("## YouTube Downloader")
    gr.Markdown("Paste a YouTube link, choose format, then download.")

    url_input = gr.Textbox(
        label="YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    format_choice = gr.Dropdown(
        choices=[
            "Video Best Quality",
            "Video 1080p (if available)",
            "Audio (MP3)",
        ],
        value="Video Best Quality",
        label="Format",
    )

    download_button = gr.Button("Download", variant="primary")
    status_output = gr.Textbox(label="Status", interactive=False)
    file_output = gr.File(label="Downloaded File")

    download_button.click(
        fn=_download,
        inputs=[url_input, format_choice],
        outputs=[status_output, file_output],
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    demo.launch(server_name="0.0.0.0", server_port=port)
