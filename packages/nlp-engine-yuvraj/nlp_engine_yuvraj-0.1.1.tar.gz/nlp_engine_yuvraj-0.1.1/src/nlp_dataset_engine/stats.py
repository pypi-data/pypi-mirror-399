import time
from typing import Dict, Any

class DatasetStats:
    """
    Tracks real-time statistics during ingestion.
    """
    def __init__(self):
        self.total_processed = 0
        self.valid_count = 0
        self.dropped_count = 0
        self.start_time = time.time()

    def update(self, is_valid: bool):
        """
        Update counters for a single row.
        """
        self.total_processed += 1
        if is_valid:
            self.valid_count += 1
        else:
            self.dropped_count += 1

    def get_report(self) -> Dict[str, Any]:
        """
        Generate a summary report.
        """
        elapsed = time.time() - self.start_time
        drop_rate = 0.0
        if self.total_processed > 0:
            drop_rate = (self.dropped_count / self.total_processed) * 100

        rows_per_sec = 0
        if elapsed > 0:
            rows_per_sec = int(self.total_processed / elapsed)

        return {
            "total_processed": self.total_processed,
            "valid_rows": self.valid_count,
            "dropped_rows": self.dropped_count,
            "drop_rate_percent": round(drop_rate, 2),
            "elapsed_seconds": round(elapsed, 2),
            "speed_rows_per_sec": rows_per_sec
        }