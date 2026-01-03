import os
import gzip
import pytest
from nlp_dataset_engine.hashing import calculate_sha256
from nlp_dataset_engine.compression import smart_open

def test_hashing(tmp_path):
    # Create a dummy file
    f = tmp_path / "test_hash.txt"
    f.write_text("hello world", encoding="utf-8")
    
    # known sha256 for "hello world"
    expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    
    assert calculate_sha256(str(f)) == expected_hash

def test_smart_open_read(tmp_path):
    # 1. Test regular file
    reg_file = tmp_path / "plain.txt"
    reg_file.write_text("plain text", encoding="utf-8")
    
    with smart_open(str(reg_file), "r") as f:
        assert f.read() == "plain text"

    # 2. Test GZIP file
    gz_file = tmp_path / "compressed.txt.gz"
    with gzip.open(gz_file, "wt", encoding="utf-8") as f:
        f.write("compressed text")
        
    with smart_open(str(gz_file), "r") as f:
        assert f.read() == "compressed text"