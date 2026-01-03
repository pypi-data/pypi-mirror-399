import json
from pathlib import Path
from typing import Generator, Dict, Union, List
from .validators import DataValidator

class DatasetLoader:
    """
    A memory-efficient loader for NLP datasets with validation and observability.
    """

    def __init__(self, source_path: str, min_length: int = 10):
        self.source_path = Path(source_path)
        self.validator = DataValidator(min_length=min_length)
        # Observability: Track what happens
        self.stats = {
            "total_processed": 0,
            "dropped_too_short": 0,
            "valid_yielded": 0
        }
        
        if not self.source_path.exists():
            raise FileNotFoundError(f"Path not found: {source_path}")

    def stream_data(self) -> Generator[Dict[str, str], None, None]:
        """Lazy-loads and VALIDATES data line by line."""
        # Reset stats at start of stream
        self.stats = {k: 0 for k in self.stats}
        
        if self.source_path.is_file():
            yield from self._process_file(self.source_path)
        else:
            for file_path in self.source_path.glob("*.txt"):
                yield from self._process_file(file_path)

    def _process_file(self, file_path: Path) -> Generator[Dict[str, str], None, None]:
        """Helper to read and filter a single file."""
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                self.stats["total_processed"] += 1
                
                clean_line = line.strip()
                record = {"text": clean_line, "source": file_path.name}
                
                if self.validator.validate(record):
                    self.stats["valid_yielded"] += 1
                    yield record
                else:
                    self.stats["dropped_too_short"] += 1

    def export_to_jsonl(self, output_path: str) -> Dict[str, int]:
        """
        Writes valid data to a JSONL file and returns final stats.
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out, "w", encoding="utf-8") as f:
            for record in self.stream_data():
                f.write(json.dumps(record) + "\n")
        
        return self.stats