import json
import os
from typing import Iterator, Dict, Any

class JSONLWriter:
    """
    Writes stream data to a JSONL file efficiently.
    """
    def __init__(self, output_path: str):
        self.output_path = output_path

    def write_stream(self, data_stream: Iterator[Dict[str, Any]]) -> int:
        """
        Consumes the stream and writes to disk line-by-line.
        Returns the count of lines written.
        """
        count = 0
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for item in data_stream:
                f.write(json.dumps(item) + '\n')
                count += 1
        return count