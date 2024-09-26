import ast
import bs4
import requests
from urllib.parse import urlparse, parse_qs, quote
from utils import ENDPOINT, HEADERS, WORKINFO_ENDPOINT
from bs4 import BeautifulSoup, Tag


class AsmrOne:
    def __init__(self, url) -> None:
        self.url = url
        self.code = self.get_code(url)
        self.path = self.get_path(url)
        self.data = None

    def get_path(self, url: str) -> list:
        try:
            parsed_url = urlparse(url)
            query_dict = parse_qs(parsed_url.query)
            path_list = query_dict["path"]
            return ast.literal_eval(path_list[0])
        except (KeyError, ValueError):
            # No path query parameter or not a valid list expression
            return []

    def get_code(self, url: str):
        path = urlparse(url).path
        code = path.split("/")[-1]
        return code.replace("RJ", "")

    def get_work(self, code: str):
        if self.data is None:
            self.data = requests.get(ENDPOINT + code, headers=HEADERS).json()
        return self.data

    def get_thumbnail(self):
        return requests.get(url=WORKINFO_ENDPOINT + self.code, headers=HEADERS).json()[
            "mainCoverUrl"
        ]

    def get_track_urls(self) -> list:
        map = self.path

        data = self.data
        if data is None:
            data = self.get_work(self.code)

        for folder in map:
            for item in data:
                if item["title"] == folder:
                    data = item["children"]

        return data


class JapaneseAsmr:
    def __init__(self, url):
        self.url = url
        self._thumburl = None
        self._tracks = None
        self._code = None
        self._page = None

    def _get_page(self):
        if self._page is None:
            resp = requests.get(self.url)
            self._page = BeautifulSoup(resp.text, "html.parser")
        return self._page

    @property
    def thumburl(self):
        return f"https://pic.weeabo0.xyz/{self.code}_img_main.jpg"

    @property
    def code(self):
        if self._code is None:
            content = self._get_page().select_one(".entry-content")
            if content is not None:
                for i in content.find_all("p"):
                    if type(i) is bs4.element.Tag and "RJ Code:" in i.text:
                        self._code = i.text.removeprefix("RJ Code:").strip()

        return self._code

    @property
    def tracks(self):
        if self._tracks is None:
            tracks = []
            audiosContainer = self._get_page().select_one("div.audio_main")
            if audiosContainer is None:
                raise Exception("could not find audio div")

            for i in audiosContainer:
                if type(i) is not Tag:
                    continue

                if i.name == "p" and i.text:
                    title = i.text
                    audio = i.nextSibling
                    if type(audio) is not Tag:
                        raise Exception("failed to get audio: Audio is not of type Tag")
                    if audio.name != "audio":
                        raise Exception(f"failed to get audio for {title}")

                    source = audio.find("source")
                    if type(source) is not Tag:
                        raise Exception(
                            f"failed to get source for {title}: source is not of type Tag"
                        )

                    link = quote(source.attrs["src"].removeprefix("https://"))

                    tracks.append(
                        {"title": title, "mediaDownloadUrl": "https://" + link}
                    )

                self._tracks = tracks

        return self._tracks
