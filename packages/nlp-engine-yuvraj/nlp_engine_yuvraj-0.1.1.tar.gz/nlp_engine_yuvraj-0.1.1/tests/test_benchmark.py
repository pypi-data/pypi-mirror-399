import pytest
import os
import json
from nlp_dataset_engine.benchmark import BenchmarkRunner

def test_benchmark_runner(tmp_path):
    # 1. Create a dummy CSV file with 1000 lines
    f = tmp_path / "bench_data.csv"
    content = "text\n" + "\n".join([f"This is performance test line {i}" for i in range(1000)])
    f.write_text(content, encoding="utf-8")
    
    # 2. Run the benchmark
    runner = BenchmarkRunner(str(f), text_col="text")
    results = runner.run()
    
    # 3. Verify the math
    assert results["total_rows"] == 1000
    assert results["rows_per_second"] > 0
    assert "duration_seconds" in results
    
    # 4. Verify report saving
    report_path = tmp_path / "report.json"
    runner.save_report(results, str(report_path))
    
    assert report_path.exists()
    with open(report_path) as f:
        saved_data = json.load(f)
        assert saved_data["total_rows"] == 1000
        