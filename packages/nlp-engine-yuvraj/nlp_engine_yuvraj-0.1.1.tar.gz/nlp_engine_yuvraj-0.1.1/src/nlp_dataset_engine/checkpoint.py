import os
from typing import Set

class CheckpointManager:
    """
    Tracks which files have been successfully processed to allow resuming.
    """
    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
        self.processed_files: Set[str] = self._load()

    def _load(self) -> Set[str]:
        """Loads the list of processed file paths from disk."""
        if not os.path.exists(self.checkpoint_file):
            return set()
        
        with open(self.checkpoint_file, "r", encoding="utf-8") as f:
            # We use absolute paths to be safe
            return set(line.strip() for line in f if line.strip())

    def is_done(self, file_path: str) -> bool:
        """Checks if a file has already been processed."""
        return os.path.abspath(file_path) in self.processed_files

    def mark_done(self, file_path: str):
        """Marks a file as processed and saves it to disk immediately."""
        abs_path = os.path.abspath(file_path)
        if abs_path not in self.processed_files:
            self.processed_files.add(abs_path)
            with open(self.checkpoint_file, "a", encoding="utf-8") as f:
                f.write(abs_path + "\n")