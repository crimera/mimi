from yabe import Yabe
import argparse
import urllib.parse


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--lang", type=str, default="ja", help="source language")
parser.add_argument("--task", type=str, default="translate", help="task translate | transcribe")
parser.add_argument("--thumbnail", type=str, default="", help="path to thumbnail")
parser.add_argument("input_or_url", type=str, help="the file to transcribe")

args = parser.parse_args()

inpt = args.input_or_url
lang = args.lang
task = args.task
thumbnail = args.thumbnail

model = Yabe("tiny", task=task)

host = urllib.parse.urlparse(inpt).netloc

if host == 'asmr.one':
    pass
elif not host:
    model.transcribe_and_embed(inpt, thumbnail, lang)
