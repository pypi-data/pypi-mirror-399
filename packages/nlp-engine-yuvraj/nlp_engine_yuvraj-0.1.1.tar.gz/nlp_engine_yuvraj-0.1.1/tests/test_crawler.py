import pytest
import os
from nlp_dataset_engine.crawler import FileCrawler

def test_find_files_recursive(tmp_path):
    """
    Test if crawler finds files in nested subdirectories.
    Structure:
    /root
      - file1.csv
      - ignored.jpg
      /subdir
        - file2.TXT
    """
    # 1. Setup fake directory
    d = tmp_path / "subdir"
    d.mkdir()
    
    p1 = tmp_path / "file1.csv"
    p1.write_text("content")
    
    p2 = tmp_path / "ignored.jpg"
    p2.write_text("content")
    
    p3 = d / "file2.TXT" # Test case-insensitivity (.TXT vs .txt)
    p3.write_text("content")
    
    # 2. Run Crawler
    crawler = FileCrawler(extensions=[".csv", ".txt"])
    found_files = list(crawler.find_files(str(tmp_path)))
    
    # 3. Assertions
    assert len(found_files) == 2
    # Check that filenames match (ignoring full path for simpler check)
    filenames = [os.path.basename(f) for f in found_files]
    assert "file1.csv" in filenames
    assert "file2.TXT" in filenames
    assert "ignored.jpg" not in filenames
    