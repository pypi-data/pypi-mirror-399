import gzip
import io
from typing import IO

def smart_open(filename: str, mode: str = "r") -> IO:
    """
    Opens a file with GZIP compression if the filename ends in .gz,
    otherwise opens it as a standard text file.
    """
    # Force text mode and utf-8 for consistency
    if "b" not in mode:
        encoding = "utf-8"
    else:
        encoding = None

    if filename.endswith(".gz"):
        # gzip.open handles compression transparently
        return gzip.open(filename, mode + "t", encoding=encoding) # 't' for text mode
    else:
        return open(filename, mode, encoding=encoding)