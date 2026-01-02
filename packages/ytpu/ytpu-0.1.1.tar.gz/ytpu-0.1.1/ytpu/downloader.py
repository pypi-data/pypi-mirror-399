# downloader.py

import subprocess
import json
import os
import logging

from tqdm import tqdm


def get_playlist_info(url) -> dict:
    cmd = ["yt-dlp", "--flat-playlist", "-J", url]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Error in request {url} due to {result.stderr}")

    try:
        return json.loads(result.stdout)
    except Exception as e:
        raise SyntaxError(f"Failed to convert to JSON due to {e}")


def download_videos(videos: list[dict], args: dict):
    for i in tqdm(range(len(videos)), desc="Downloading videos"):
        video = videos[i]
        output_path = os.path.join(args["output_folder"], f"{video['title']}.m4a")
        cmd = [
            "yt-dlp",
            "--embed-thumbnail",
            "-f",
            "bestaudio[ext=m4a]",
            "--output",
            output_path,
            video["url"],
        ]

        logging.info(f"CMD: ' '.join({cmd})")

        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode != 0:
            logging.info("FAIL")
        else:
            logging.info("OK")
