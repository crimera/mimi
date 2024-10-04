from pathlib import Path
from utils import JAPANESEASMR_HOST, download
from urllib.parse import urlparse
from hosts import AsmrOne, JapaneseAsmr
from yabe import StableWhisper, Yabe
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--lang", type=str, default="ja", help="source language")
parser.add_argument(
    "--task", type=str, default="translate", help="task translate | transcribe"
)
parser.add_argument("--thumbnail", type=str, default="", help="path to thumbnail")
parser.add_argument("--model", type=str, help="path or size of model")
parser.add_argument("input_or_url", type=str, help="the file to transcribe")
parser.add_argument("--temperature", type=float, default=0, help="convert wav file to opus")
parser.add_argument("--beam_size", type=int, default=5)
parser.add_argument("--wav_to_opus", type=int, default=True, help="convert wav file to opus")
parser.add_argument("--clean_audio", type=str, default="", help="Add a clean audio for transcript, the input audio will still be used for embed")

args = parser.parse_args()

inpt = args.input_or_url
lang = args.lang
task = args.task
model = args.model
thumbnail = args.thumbnail
to_opus = args.wav_to_opus
temperature = args.temperature
beam_size = args.beam_size
clean_audio = args.clean_audio

model = StableWhisper(model, task=task, temperature=temperature)

try:
    host = urlparse(inpt).netloc
except Exception:
    host = ""


def download_and_transcribe(i, thumbnail, referer=None):
    link = i["mediaDownloadUrl"]
    name = i["title"]
    download(link, path, referer=referer)
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

        if clean_audio:
            clean_audio_work = AsmrOne(clean_audio)

            clean_audio_path = path+"clean/"
            if not Path(clean_audio_path).exists():
                Path(clean_audio_path).mkdir(parents=True, exist_ok=True)

            clean_audio_links = clean_audio_work.get_track_urls()
            clean_audios = [x for x in links if x["type"]=="audio"]

            for i in clean_audios:
                link = i["mediaDownloadUrl"]
                name = i["title"]

                download(link, clean_audio_path)
                model.transcribe(f"{clean_audio_path}{name}", lang)

            for i in audios:
                link = i["mediaDownloadUrl"]
                name = i["title"]
                download(link, path)
                model.embed(f"{path}{name}", Path(f"{clean_audio_path}{name}").with_suffix(".srt"))
        else:
            for i in audios:
                download_and_transcribe(i, thumbnail)
elif host == "japaneseasmr.com":
        work = JapaneseAsmr(inpt)
        path = f"{work.code}/"

        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)

        thumbnail = download(work.thumburl, path, JAPANESEASMR_HOST)

        audios = work.tracks
        if audios is None:
            raise Exception("No audios found")

        for i in audios:
            name = download(i["mediaDownloadUrl"], path, JAPANESEASMR_HOST)
            print("Start transcribing...")
            model.transcribe_and_embed(f"{name}", thumbnail, lang, to_opus)
elif host == "":
    model.transcribe_and_embed(inpt)
else :
        filename = download(inpt)

        model.transcribe_and_embed(filename)
