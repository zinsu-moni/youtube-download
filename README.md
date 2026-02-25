# YouTube Downloader (Python + Nice UI)

Simple desktop YouTube downloader built with Python, `yt-dlp`, and `customtkinter`.

Also includes a hostable web UI using Gradio.

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

## Run Web App (Hostable)

```bash
python web_app.py
```

Open:

```text
http://127.0.0.1:7860
```

## Host on Render / Railway

1. Push this folder to a GitHub repository.
2. Create a new Web Service on Render (or a new Project on Railway).
3. Use:
	- Build command: `pip install -r requirements.txt`
	- Start command: `python web_app.py`
4. Deploy.

The app already reads `PORT` from environment variables.

## Notes

- If a download fails, confirm the URL is valid and public.
- For best reliability, keep `yt-dlp` updated:

```bash
pip install -U yt-dlp
```
