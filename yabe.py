from io import StringIO
import subprocess
from faster_whisper import WhisperModel
import stable_whisper
from pathlib import Path

from utils import time, convert_to_opus


class Yabe:
    def __init__(
        self,
        model_size_or_path: str,
        beam_size: int = 5,
        vad_filter: bool = True,
        task="translate",
        temperature: float = 0.5,
    ) -> None:
        self.beam_size = beam_size
        self.task = task
        self.vad_filter = vad_filter
        self.temerature = temperature

        self.model = WhisperModel(model_size_or_path, num_workers=2)

    def transcribe(self, filename: str, lang: str = "ja"):
        srt = Path(filename).with_suffix(".srt")

        if srt.exists():
            print(f"{srt} exists\nskipping transcribe")
            return

        segments, info = self.model.transcribe(
            filename,
            beam_size=self.beam_size,
            task=self.task,
            vad_filter=self.vad_filter,
            temperature=self.temerature,
        )

        if not lang:
            print(
                "Detected language '%s' with probability %f"
                % (info.language, info.language_probability)
            )

        lines = StringIO()

        for i, segment in enumerate(segments):
            start = time(segment.start)
            end = time(segment.end)
            text = segment.text.lstrip()
            srt_line = f"\n{i + 1}\n{start},000 --> {end},000\n{text}\n"

            print(srt_line)
            lines.write(srt_line)

        srt.write_text(lines.getvalue())

    def embed(self, filename: str, srt: Path, thumbnail: str = "", to_opus: bool = False):
        out = Path(filename).with_suffix(".mkv")

        if thumbnail and Path(thumbnail).exists():
            thumbnail = f'--attach-file "{thumbnail}"'

        if filename.endswith("wav") and to_opus:
            print(f"Converting {filename} to opus")
            filename = convert_to_opus(filename)

        subprocess.Popen(
            f'mkvmerge "{filename}" "{srt}" {thumbnail} -o "{out}"', shell=True
        )

        return out

    def transcribe_and_embed(
        self, filename: str, thumbnail: str = "", lang: str = "ja", to_opus: bool = False
    ):
        self.transcribe(filename, lang)
        srt = Path(filename).with_suffix(".srt")
        return self.embed(filename, srt, thumbnail, to_opus)

class StableWhisper(Yabe):
    def __init__(self, model_size_or_path: str, beam_size: int = 5, vad_filter: bool = True, task="translate", temperature: float = 0.5) -> None:
        self.beam_size = beam_size
        self.task = task
        self.vad_filter = vad_filter
        self.temerature = temperature

        self.model = stable_whisper.load_faster_whisper(model_size_or_path)

    def transcribe(self, filename: str, lang: str = "ja"):
        srt = Path(filename).with_suffix(".srt")

        if srt.exists():
            print(f"{srt} exists\nskipping transcribe")
            return

        result = self.model.transcribe_stable(audio=filename, language=lang, vad_filter=self.vad_filter, word_timestamps=False, task=self.task)
        result.to_srt_vtt(str(srt))
