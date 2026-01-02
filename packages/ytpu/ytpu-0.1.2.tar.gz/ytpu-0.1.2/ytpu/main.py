# main.py

import sys
import os
import logging
from pathlib import Path
from pathvalidate import sanitize_filename

import ytpu.downloader as dl
from ytpu.file_io import load_json, write_json  # noqa: F401


EXT = ".m4a"
APP_NAME = "ytpu"
DATA_DIR = (
    Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME
)
LOG_FILE = DATA_DIR / "ytpu.log"
TEMP_JSON = DATA_DIR / "temp.json"


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,  # log to a file
        filemode="a",  # append mode
        format="%(asctime)s - %(levelname)s - %(message)s",  # simple format
        datefmt="%Y-%m-%d %H:%M:%S",  # date format
        level=logging.INFO,  # default logging level
    )


def init_app():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def validate_url(url: str):
    pass


def validate_path(path: str):
    if not os.path.exists(path):
        raise FileExistsError(f"Path {path} does not exist.")


def get_args():
    args = {"output_folder": ".", "url": ""}
    if len(sys.argv) == 2:
        if sys.argv[1] == "-v" or sys.argv[1] == "--version":
            from importlib.metadata import version

            print(version(APP_NAME))

        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print("ytpu -o [OUTPUT_FOLDER] [URL]")
            print("ytpu [URL]")
        else:
            args["url"] = sys.argv[1]
    elif len(sys.argv) == 4:
        if sys.argv[1] == "-o":
            args["output_folder"] = sys.argv[2]
            args["url"] = sys.argv[3]
        elif sys.argv[2] == "-o":
            args["output_folder"] = sys.argv[3]
            args["url"] = sys.argv[1]
    else:
        raise SyntaxError(f"Expected 2 or 4 arg. Got {len(sys.argv)}")
    validate_path(args["output_folder"])
    validate_url(args["url"])
    return args


def get_local_videos(folder_path):
    files = os.listdir(folder_path)
    all_files = []

    for file in files:
        file = str(file)
        # check is not folder
        if not os.path.isfile(os.path.join(folder_path, file)):
            continue

        # check file is fully download
        if not file.endswith(EXT):
            continue

        all_files.append(file.replace(EXT, ""))
    return all_files


def extract_video_from_playlist(data: dict) -> list:
    if "entries" not in data:
        raise KeyError("'entries' not in JSON result.")

    videos = []
    for entry in data["entries"]:
        if "url" not in entry:
            print("WARNING: 'url' not in JSON entry.")
            continue
        if "title" not in entry:
            print("WARNING: 'title' not in JSON entry")
            continue
        url = entry["url"]
        title = sanitize_filename(entry["title"])
        videos.append({"url": url, "title": title})
    return videos


def remove_local_videos(local_videos: list, remote_videos: list) -> list[dict]:
    videos_to_dl = []
    for rv in remote_videos:
        match = False
        for lv in local_videos:
            if lv == rv["title"]:
                match = True
                break
        if not match:
            videos_to_dl.append(rv)
    return videos_to_dl


def main():
    print("Welcome to ytpu")

    init_app()

    # parse args input
    args = get_args()
    print(f"INPUT URL: {args['url']}\nINPUT OUTPUT_PATH: {args['output_folder']}")

    # find local videos
    local_videos = get_local_videos(args["output_folder"])
    print(f"Found {len(local_videos)} videos in local folder")

    # get videos from playlist
    data = dl.get_playlist_info(args["url"])
    write_json(TEMP_JSON, data, mode="w")

    remote_videos = extract_video_from_playlist(data)
    print(f"Found {len(remote_videos)} videos in playlist")

    videos_to_dl = remove_local_videos(local_videos, remote_videos)
    print(f"Found {len(videos_to_dl)} videos in playlist not already downloaded")

    dl.download_videos(videos_to_dl, args)
