import requests
import ast
import yt_dlp
from pathlib import Path
from os.path import exists
from urllib.parse import unquote, urlparse, parse_qs
from utils import ENDPOINT, HEADERS, WORKINFO_ENDPOINT

class AsmrOne():
    def __init__(self, url) -> None:
        self.url = url
        self.code = self.get_code(url)
        self.path = self.get_path(url)
        self.data = None

    def get_path(self, url: str):
        try:
            parsed_url = urlparse(url)
            query_dict = parse_qs(parsed_url.query)
            path_list = ast.literal_eval(query_dict['path'][0])
            return path_list
        except (KeyError, ValueError):
            # No path query parameter or not a valid list expression
            return []

    def get_code(self, url: str):
        path = urlparse(url).path
        code = path.split('/')[-1]
        return code.replace('RJ', '')

    def get_work(self, code: str):
        if self.data is None:
            self.data = requests.get(
                ENDPOINT + code,
                headers=HEADERS
            ).json()
        return self.data

    def get_thumbnail(self):
        return requests.get(
            url = WORKINFO_ENDPOINT + self.code,
            headers=HEADERS
        ).json()['mainCoverUrl']

    def get_track_urls(self, path=None, data=None):
        if path is None:
            path = self.path

        if data is None:
            data = self.get_work(self.code)

        if len(path) == 0:
            return data
        for child in data:
            if child['title'] == path[0]:
                del path[0]
                return self.get_track_urls(path, child['children'])
        return data