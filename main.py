from pathlib import Path
from utils import is_supported
from yabe import Yabe
import argparse
import urllib.parse
from yt_dlp import YoutubeDL


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--lang", type=str, default="ja", help="source language")
parser.add_argument("--task", type=str, default="translate", help="task translate | transcribe")
parser.add_argument("--thumbnail", type=str, default="", help="path to thumbnail")
parser.add_argument("--model", type=str, help="path or size of model")
parser.add_argument("input_or_url", type=str, help="the file to transcribe")

args = parser.parse_args()

inpt = args.input_or_url
lang = args.lang
task = args.task
model = args.model
thumbnail = args.thumbnail

model = Yabe(model, task=task)
host = urllib.parse.urlparse(inpt).netloc

if host == 'asmr.one':
    pass
elif not host:
    model.transcribe_and_embed(inpt, thumbnail, lang)

if is_supported(inpt):
    print("youtube")

    ydl_opts = {
        'final_ext': 'opus',
        'format': 'bestaudio/best',
        'postprocessors':
            [{
                'format': 'jpg',
                'key': 'FFmpegThumbnailsConvertor',
                'when': 'before_dl'},
             {
                 'key': 'FFmpegExtractAudio',
                 'nopostoverwrites': False,
                 'preferredcodec': 'best',
                 'preferredquality': '5'
              }],
        'writethumbnail': True}

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(inpt, download=True)
        file_path = ydl.prepare_filename(info) 

    filename = Path(file_path).with_suffix(".opus")
    thumbnail = Path(file_path).with_suffix(".jpg")
    model.transcribe_and_embed(f"{filename}", f"{thumbnail}", lang)
