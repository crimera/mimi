from pathlib import Path
from utils import download
from urllib.parse import urlparse
from hosts import AsmrOne
from yabe import Yabe
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--lang", type=str, default="ja", help="source language")
parser.add_argument(
    "--task", type=str, default="translate", help="task translate | transcribe"
)
parser.add_argument("--thumbnail", type=str, default="", help="path to thumbnail")
parser.add_argument("--model", type=str, help="path or size of model")
parser.add_argument("input_or_url", type=str, help="the file to transcribe")
parser.add_argument("--pools", type=int, default=2, help="path to thumbnail")
parser.add_argument(
    "--temperature", type=int, default=0.5, help="convert wav file to opus"
)
parser.add_argument(
    "--wav_to_opus", type=int, default=True, help="convert wav file to opus"
)

args = parser.parse_args()

inpt = args.input_or_url
lang = args.lang
task = args.task
model = args.model
thumbnail = args.thumbnail
pools = args.pools
to_opus = args.wav_to_opus
temperature = args.temperature

model = Yabe(model, task=task, temperature=temperature)
host = urlparse(inpt).netloc


def download_and_transcribe(i):
    link = i["mediaDownloadUrl"]
    name = i["title"]
    download(link, path)
    print("Start transcribing...")
    model.transcribe_and_embed(f"{path}{name}", thumbnail, lang, to_opus)


if host == "asmr.one":
    work = AsmrOne(inpt)
    path = f"RJ{work.code}/"

    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)

    links = work.get_track_urls()
    thumbnail = download(work.get_thumbnail(), path)

    audios = [x for x in links if x["type"] == "audio"]

    for i in audios:
        download_and_transcribe(i)
