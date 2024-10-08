from datetime import timedelta
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
import requests
import yt_dlp
import os.path

from yt_dlp.cookies import subprocess


ENDPOINT = "https://api.asmr-100.com/api/tracks/"
WORKINFO_ENDPOINT = "https://api.asmr-100.com/api/work/"
JAPANESEASMR_HOST = "https://japaneseasmr.com/"
USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58"
HEADERS = {"User-Agent": USERAGENT}


def time(seconds):
    tdelta = timedelta(seconds=seconds)
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def is_supported(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != "generic":
            return True
    return False


def get_filename_from_url(_url: str) -> str:
    # Get filename from content-disposition
    r = requests.get(_url, allow_redirects=True)
    cd = r.headers.get("content-disposition")
    if not cd or "filename=" not in cd:
        return unquote(urlparse(_url).path.split("/")[-1])
    filename = re.findall("filename=(.+)", cd)
    if len(filename) == 0:
        raise Exception("Filename not found")
    return filename[0]

def convert_to_opus(filename: str) -> str:
    out = Path(filename).with_suffix(".opus")

    if os.path.exists(str(out)):
        print("Opus file already exists, skipping...")
        return str(out)

    subprocess.run(f'ffmpeg -i "{filename}" -c:a libopus -b:a 128k "{out}"', shell=True, check=True)
    return str(out)


def download(url: str, path: str = "", referer=None) -> str:
    headers = HEADERS.copy()
    if referer:
        headers["Referer"] = referer

    response = requests.get(url, stream=True, headers=headers)
    filename = path + get_filename_from_url(url)

    if os.path.exists(filename):
        print("File already exists, cancelling download...")
        return filename

    print(f"Downloading {filename}")

    with open(filename, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)

    return filename
