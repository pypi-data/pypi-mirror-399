import os
import glob
from typing import Iterator, List

class FileCrawler:
    """
    Recursively finds all supported files in a directory.
    """
    def __init__(self, extensions: List[str] = None):
        if extensions is None:
            extensions = [".csv", ".txt"]
        self.extensions = [ext.lower() for ext in extensions]

    def find_files(self, root_path: str) -> Iterator[str]:
        """
        Yields file paths matching the extensions recursively.
        """
        # Case 1: If input is just a single file, return it
        if os.path.isfile(root_path):
            if any(root_path.lower().endswith(ext) for ext in self.extensions):
                yield root_path
            return

        # Case 2: Crawl directory
        for root, _, files in os.walk(root_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.extensions):
                    yield os.path.join(root, file)
                    