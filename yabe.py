from io import StringIO
import subprocess
from faster_whisper import WhisperModel
from pathlib import Path
from utils import time


class Yabe():
    def __init__(self, model_size_or_path: str, beamsize: int = 5,
                 vad_filter: bool = True, task="translate") -> None:

        self.beamsize = beamsize
        self.task = task
        self.vad_filter = vad_filter

        self.model = WhisperModel(model_size_or_path, num_workers=2)

    def transcribe(self, filename: str, lang: str = "ja"):
        srt = Path(filename).with_suffix(".srt")

        if srt.exists():
            print(f"{srt} exists\nskipping transcribe")
            return

        segments, info = self.model.transcribe(
            filename,
            beam_size=self.beamsize,
            task=self.task,
            vad_filter=self.vad_filter
        )

        if not lang:
            print("Detected language '%s' with probability %f" %
                  (info.language, info.language_probability))

        lines = StringIO()

        for i, segment in enumerate(segments):
            start = time(segment.start)
            end = time(segment.end)
            text = segment.text.lstrip()
            srt_line = f"\n{i + 1}\n{start},000 --> {end},000\n{text}\n"

            print(srt_line)
            lines.write(srt_line)

        srt.write_text(lines.getvalue())

    def embed(self, filename: str, thumbnail: str = ""):
        srt = Path(filename).with_suffix(".srt")
        out = Path(filename).with_suffix(".mkv")

        if thumbnail:
            thumbnail = f'--attach-file "{thumbnail}"'

        subprocess.Popen(
            f'mkvmerge "{filename}" "{srt}" {thumbnail} -o "{out}"',
            shell=True
        )

        return out

    def transcribe_and_embed(self, filename: str, thumbnail: str,
                             lang: str = "ja"):
        self.transcribe(filename, lang)
        return self.embed(filename, thumbnail)
