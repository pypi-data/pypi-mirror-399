import time
import json
import os
from typing import Dict, Any
from .streamer import DatasetStreamer
from .validators import DataValidator

class BenchmarkRunner:
    """
    Measures the raw throughput (rows/sec and bytes/sec) of the engine.
    """
    def __init__(self, input_path: str, text_col: str = "text"):
        self.input_path = input_path
        self.text_col = text_col
        self.validator = DataValidator(min_length=1) # Minimal validation for speed test

    def run(self) -> Dict[str, Any]:
        print(f"🏎️  Benchmarking: {self.input_path} ...")
        
        start_time = time.time()
        
        row_count = 0
        total_bytes = 0
        
        # We process but DO NOT write to disk, to measure pure engine speed
        streamer = DatasetStreamer(self.input_path, text_column=self.text_col)
        
        for row in streamer.stream():
            # Validate to simulate real work
            if self.validator.validate(row):
                row_count += 1
                # Estimate size roughly
                total_bytes += len(json.dumps(row))
                
            if row_count % 10000 == 0 and row_count > 0:
                print(f"   ... processed {row_count} rows", end="\r")

        end_time = time.time()
        duration = end_time - start_time
        
        if duration == 0: duration = 0.001 # Prevent zero division

        results = {
            "timestamp": time.time(),
            "input_file": self.input_path,
            "total_rows": row_count,
            "duration_seconds": round(duration, 4),
            "rows_per_second": round(row_count / duration, 2),
            "mb_per_second": round((total_bytes / 1024 / 1024) / duration, 2)
        }
        
        return results

    def save_report(self, results: Dict[str, Any], output_path: str = "benchmark.json"):
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Benchmark saved to: {output_path}")
        