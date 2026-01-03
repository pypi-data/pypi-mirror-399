import os
import json
from typing import Dict, Any
from .compression import smart_open

class ShardedWriter:
    """
    Writes data into multiple split files (shards).
    Supports optional GZIP compression via smart_open.
    """
    def __init__(self, output_prefix: str, shard_size: int = 10000, compress: bool = False):
        self.output_prefix = output_prefix
        self.shard_size = shard_size
        self.compress = compress  # New flag
        self.current_shard_index = 0
        self.current_count = 0
        self.file_handle = None
        self._open_new_shard()

    def _get_shard_filename(self) -> str:
        # Add .gz extension if compression is requested
        ext = ".jsonl.gz" if self.compress else ".jsonl"
        return f"{self.output_prefix}-{self.current_shard_index:04d}{ext}"

    def _open_new_shard(self):
        """Closes current file and opens the next shard."""
        if self.file_handle:
            self.file_handle.close()
        
        filename = self._get_shard_filename()
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Use our new helper from compression.py
        self.file_handle = smart_open(filename, "w")
            
        self.current_count = 0
        print(f"   --> Writing to shard: {os.path.basename(filename)}")

    def write_item(self, item: Dict[str, Any]):
        """Writes a single item, rotating shards if necessary."""
        if self.current_count >= self.shard_size:
            self.current_shard_index += 1
            self._open_new_shard()
            
        self.file_handle.write(json.dumps(item) + "\n")
        self.current_count += 1

    def close(self):
        if self.file_handle:
            self.file_handle.close()