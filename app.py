from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from downloader import YouTubeDownloader


class DownloaderApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("760x460")
        self.minsize(700, 420)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.downloader = YouTubeDownloader()
        self.ui_queue: queue.Queue[tuple[str, str | float]] = queue.Queue()

        self._build_ui()
        self.after(100, self._process_ui_queue)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, corner_radius=14)
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            container,
            text="YouTube Downloader",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=24, pady=(22, 6), sticky="w")

        subtitle = ctk.CTkLabel(
            container,
            text="Paste a YouTube link, choose format, and download.",
            text_color=("gray25", "gray75"),
        )
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="w")

        self.url_entry = ctk.CTkEntry(
            container,
            height=40,
            placeholder_text="https://www.youtube.com/watch?v=...",
        )
        self.url_entry.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))

        options_frame = ctk.CTkFrame(container, fg_color="transparent")
        options_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 12))
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)

        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=[
                "Video Best Quality",
                "Video 1080p (if available)",
                "Audio (MP3)",
            ],
            height=38,
        )
        self.format_menu.set("Video Best Quality")
        self.format_menu.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.path_entry = ctk.CTkEntry(options_frame, height=38)
        self.path_entry.insert(0, str(Path.home() / "Downloads"))
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        browse_btn = ctk.CTkButton(
            container,
            text="Choose Folder",
            height=38,
            command=self._pick_folder,
        )
        browse_btn.grid(row=4, column=0, padx=24, pady=(0, 12), sticky="w")

        self.progress = ctk.CTkProgressBar(container, height=16)
        self.progress.set(0)
        self.progress.grid(row=5, column=0, sticky="ew", padx=24, pady=(6, 8))

        self.status_label = ctk.CTkLabel(
            container,
            text="Idle",
            anchor="w",
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=24, pady=(0, 16))

        self.download_btn = ctk.CTkButton(
            container,
            text="Download",
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start_download,
        )
        self.download_btn.grid(row=7, column=0, padx=24, pady=(0, 22), sticky="ew")

    def _pick_folder(self) -> None:
        chosen = filedialog.askdirectory(title="Select download folder")
        if chosen:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, chosen)

    def _start_download(self) -> None:
        if self.downloader.is_downloading:
            self._set_status("A download is already running.")
            return

        url = self.url_entry.get()
        output_dir = self.path_entry.get()
        mode = self.format_menu.get()

        self.download_btn.configure(state="disabled", text="Downloading...")

        worker = threading.Thread(
            target=self.downloader.download,
            kwargs={
                "url": url,
                "output_dir": output_dir,
                "mode": mode,
                "on_progress": lambda value: self.ui_queue.put(("progress", value)),
                "on_status": lambda text: self.ui_queue.put(("status", text)),
                "on_done": lambda text: self.ui_queue.put(("done", text)),
                "on_error": lambda text: self.ui_queue.put(("error", text)),
            },
            daemon=True,
        )
        worker.start()

    def _process_ui_queue(self) -> None:
        while True:
            try:
                kind, value = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if kind == "progress":
                self.progress.set(float(value))
            elif kind == "status":
                self._set_status(str(value))
            elif kind == "done":
                self._set_status(str(value))
                self.download_btn.configure(state="normal", text="Download")
            elif kind == "error":
                self._set_status(str(value))
                self.download_btn.configure(state="normal", text="Download")

        self.after(100, self._process_ui_queue)

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
