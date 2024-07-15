import ast
import requests
from urllib.parse import urlparse, parse_qs
from utils import ENDPOINT, HEADERS, WORKINFO_ENDPOINT


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
