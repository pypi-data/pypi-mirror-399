import csv
from typing import  Iterator, Dict, Optional

class DatasetStreamer:
    """
    Memory-efficient CSV streamer.
    Reads file line-by-line using generators.
    """
    
    def __init__(self, filepath: str, text_column: str = "text"):
        self.filepath = filepath
        self.text_column = text_column

    def stream(self) -> Iterator[Dict[str, str]]:
        """
        Yields rows one by one.
        Returns a dictionary: {'text': 'actual content', 'meta': ...}
        """
        try:
            with open(self.filepath, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                
                # Check if the column actually exists
                if reader.fieldnames and self.text_column not in reader.fieldnames:
                    raise ValueError(f"Column '{self.text_column}' not found in CSV headers: {reader.fieldnames}")

                for row in reader:
                    content = row.get(self.text_column, "").strip()
                    if content:
                        yield {"text": content, "original_row": str(row)}
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.filepath}")
        except Exception as e:
            raise RuntimeError(f"Error streaming file: {str(e)}")
        