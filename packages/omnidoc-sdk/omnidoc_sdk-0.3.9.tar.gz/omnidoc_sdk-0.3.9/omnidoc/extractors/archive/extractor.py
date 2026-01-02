# omnidoc/extractors/archive/extractor.py
from omnidoc.extractors.base import BaseExtractor
import zipfile
import tempfile
import os


class ArchiveExtractor(BaseExtractor):
    def extract(self, path: str):
        extracted_files = []

        with zipfile.ZipFile(path) as z:
            tmp_dir = tempfile.mkdtemp()
            z.extractall(tmp_dir)

            for root, _, files in os.walk(tmp_dir):
                for f in files:
                    extracted_files.append(os.path.join(root, f))

        # IMPORTANT: return paths only
        return {
            "type": "archive",
            "files": extracted_files
        }
