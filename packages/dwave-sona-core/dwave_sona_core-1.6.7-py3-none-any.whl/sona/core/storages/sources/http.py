import re
from urllib.parse import unquote
from .base import SourceBase
from .youtube import YoutubeSource

try:
    import requests
except ImportError:
    pass


class HttpSource(SourceBase):
    @classmethod
    def download(cls, file):
        filename = ""
        with requests.get(file.path, stream=True) as r:
            r.raise_for_status()
            cd = r.headers.get("content-disposition")
            if cd:
                fname_match = re.findall("filename=(.+)", cd)
                if fname_match:
                    filename = fname_match[0].strip(' ";')
                    filename = unquote(filename)
            if not filename:
                filename = file.path.split("/")[-1].split("?")[0]
            if not filename:
                filename = "downloaded_file"

            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return file.mutate(path=filename)

    @classmethod
    def verify(cls, file):
        if not file.path:
            return False

        is_youtube_link = YoutubeSource.verify(file)
        if is_youtube_link:
            return False

        is_http = file.path.startswith("http://")
        is_https = file.path.startswith("https://")
        if_ftp = file.path.startswith("ftp://")
        return is_http or is_https or if_ftp
