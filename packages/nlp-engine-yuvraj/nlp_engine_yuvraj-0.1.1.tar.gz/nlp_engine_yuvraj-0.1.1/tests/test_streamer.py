import pytest
import csv
import json
import os
from nlp_dataset_engine.streamer import DatasetStreamer
from nlp_dataset_engine.validators import DataValidator
from nlp_dataset_engine.jsonl_writer import JSONLWriter
from nlp_dataset_engine.validators import DataValidator

# --- Fixtures (Setup dummy files) ---
@pytest.fixture
def sample_csv(tmp_path):
    """Creates a temporary CSV file for testing"""
    file_path = tmp_path / "test_data.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "label"])
        writer.writerow(["1", "This is a valid sentence.", "A"])
        writer.writerow(["2", "Short", "B"])  # Invalid
        writer.writerow(["3", "", "C"])       # Empty
    return str(file_path)

@pytest.fixture
def output_file(tmp_path):
    return str(tmp_path / "output.jsonl")

# --- Tests ---

def test_streamer_reads_correctly(sample_csv):
    """Test if streamer reads valid rows"""
    streamer = DatasetStreamer(sample_csv, text_column="text")
    rows = list(streamer.stream())
    
    assert len(rows) == 2  # Should read all 2 rows (validation happens later)
    assert rows[0]["text"] == "This is a valid sentence."

def test_validator_logic():
    """Test if validator filters correctly"""
    validator = DataValidator(min_length=10)
    
    valid_item = {"text": "This is long enough"}
    short_item = {"text": "Short"}
    empty_item = {"text": ""}
    
    assert validator.validate(valid_item) is True
    assert validator.validate(short_item) is False
    assert validator.validate(empty_item) is False

def test_end_to_end_pipeline(sample_csv, output_file):
    """Test the full flow: CSV -> Validate -> JSONL"""
    streamer = DatasetStreamer(sample_csv, text_column="text")
    validator = DataValidator(min_length=10)
    writer = JSONLWriter(output_file)
    
    # Run pipeline manually
    valid_stream = (row for row in streamer.stream() if validator.validate(row))
    count = writer.write_stream(valid_stream)
    
    assert count == 1  # Only 1 sentence is > 10 chars
    
    # Verify output file content
    with open(output_file, "r") as f:
        line = json.loads(f.readline())
        assert line["text"] == "This is a valid sentence."

def test_noise_filter():
    """Test rejection of text with too many symbols/numbers"""
    # Create validator with 30% noise threshold
    validator = DataValidator(max_symbol_ratio=0.3, check_english=False)
    
    # CASE 1: Clean text (100% letters) -> Should Pass
    assert validator.validate({"text": "Hello world this is clean"}) is True
    
    # CASE 2: Noisy text (>30% symbols) -> Should Fail
    # "1234567890" is 10 chars, 0 alpha. 
    assert validator.validate({"text": "1234567890"}) is False
    
    # CASE 3: Edge case
    # "a #$%^&*" -> 8 chars, 1 alpha. 1/8 = 0.125 alpha ratio (Fail)
    assert validator.validate({"text": "a #$%^&*"}) is False