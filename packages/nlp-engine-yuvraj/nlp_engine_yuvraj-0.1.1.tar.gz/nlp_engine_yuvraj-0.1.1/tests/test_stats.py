import pytest
from nlp_dataset_engine.stats import DatasetStats
from nlp_dataset_engine.validators import DataValidator

def test_stats_counting():
    """Test if stats update correctly"""
    stats = DatasetStats()
    
    # Simulate processing
    stats.update(is_valid=True)
    stats.update(is_valid=True)
    stats.update(is_valid=False) # Dropped
    
    report = stats.get_report()
    
    assert report["total_processed"] == 3
    assert report["valid_rows"] == 2
    assert report["dropped_rows"] == 1
    assert report["drop_rate_percent"] == 33.33

def test_language_validator_logic():
    """Test if validator detects non-English text"""
    # Enable English check
    validator = DataValidator(min_length=5, check_english=True)
    
    english_text = {"text": "Hello world this is English"}
    spanish_text = {"text": "Hola mundo esto es espanol"}
    
    assert validator.validate(english_text) is True
    assert validator.validate(spanish_text) is False