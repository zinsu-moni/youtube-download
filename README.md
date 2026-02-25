# YouTube Downloader (Python + Nice UI)

Simple desktop YouTube downloader built with Python, `yt-dlp`, and `customtkinter`.

## Features

- Modern dark desktop UI
- Download YouTube video in best quality or 1080p (if available)
- Download audio as MP3
- Progress bar and live status updates
- Choose any output folder

## Requirements

- Python 3.10+
- FFmpeg installed and available in PATH (needed for MP3 extraction and merging some video/audio streams)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

## Notes

- If a download fails, confirm the URL is valid and public.
- For best reliability, keep `yt-dlp` updated:

```bash
pip install -U yt-dlp
```
