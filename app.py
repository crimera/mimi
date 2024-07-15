from flask import Flask, render_template, request
from pathlib import Path
from utils import download
from urllib.parse import urlparse
from hosts import AsmrOne
from yabe import Yabe


app = Flask(__name__, static_url_path="/static")


@app.route("/")
@app.route("/index.html")
def root():
    return render_template("index.html")


def get_host(url):
    return urlparse(url).netloc


def download_and_transcribe(model, path, thumbnail, lang, to_opus, task, item):
    link = item["mediaDownloadUrl"]
    name = item["title"]
    download(link, path)
    print("Start transcribing...")
    model.transcribe_and_embed(f"{path}{name}", thumbnail, lang, to_opus)


@app.route("/submit-input", methods=["POST"])
def submit_input():
    data = request.form
    url = data["url"]

    if get_host(url) == "asmr.one":
        return render_template("asmrone.html", url=url)


@app.route("/asmrone", methods=["POST"])
def asmrone():
    data = request.form

    url = data["url"]
    model = data["model"]
    task = data["task"]
    to_opus: bool = True if data.get("to_opus") else False
    lang = data["lang"]

    work = AsmrOne(url)
    path = f"RJ{work.code}/"

    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)

    links = work.get_track_urls()
    thumbnail = download(work.get_thumbnail(), path)

    audios = [x for x in links if x["type"] == "audir"]

    model = Yabe(model, task=task, temperature=0.5)

    for i in audios:
        download_and_transcribe(model, path, thumbnail, lang, to_opus, task, i)

    return "SUCCESS"
