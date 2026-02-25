from __future__ import annotations

from pathlib import Path
from typing import Callable

from yt_dlp import YoutubeDL

ProgressCallback = Callable[[float], None]
StatusCallback = Callable[[str], None]
DoneCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]


class YouTubeDownloader:
    def __init__(self) -> None:
        self._is_downloading = False

    @property
    def is_downloading(self) -> bool:
        return self._is_downloading

    def download(
        self,
        url: str,
        output_dir: str,
        mode: str,
        on_progress: ProgressCallback,
        on_status: StatusCallback,
        on_done: DoneCallback,
        on_error: ErrorCallback,
    ) -> None:
        if self._is_downloading:
            on_error("A download is already in progress.")
            return

        url = url.strip()
        if not url:
            on_error("Please enter a YouTube URL.")
            return

        output_path = Path(output_dir).expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        ydl_opts: dict = {
            "outtmpl": str(output_path / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [
                self._build_progress_hook(on_progress=on_progress, on_status=on_status)
            ],
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

        self._is_downloading = True
        on_progress(0)
        on_status("Starting download...")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Download complete")
                on_progress(1.0)
                on_done(f"Finished: {title}")
        except Exception as exc:  # noqa: BLE001
            on_error(f"Download failed: {exc}")
        finally:
            self._is_downloading = False

    @staticmethod
    def _build_progress_hook(
        on_progress: ProgressCallback,
        on_status: StatusCallback,
    ) -> Callable[[dict], None]:
        def hook(data: dict) -> None:
            status = data.get("status")
            if status == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                downloaded = data.get("downloaded_bytes", 0)

                if total and total > 0:
                    on_progress(min(max(downloaded / total, 0), 1.0))

                speed = data.get("speed")
                if speed:
                    speed_mb = speed / (1024 * 1024)
                    on_status(f"Downloading... {speed_mb:.2f} MB/s")
                else:
                    on_status("Downloading...")

            elif status == "finished":
                on_status("Processing media...")

        return hook
