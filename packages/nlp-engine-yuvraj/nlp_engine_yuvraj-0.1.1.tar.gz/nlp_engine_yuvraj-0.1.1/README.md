# NLP Dataset Engine 

[![CI Pipeline](https://github.com/rgb-99/nlp-dataset-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/rgb-99/nlp-dataset-engine/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/nlp-engine-yuvraj)](https://pypi.org/project/nlp-engine-yuvraj/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance streaming ingestion engine for terabyte-scale NLP datasets.
Built for GSoC 2026 preparation.

## User Installation

```bash
pip install nlp-engine-yuvraj
```

## Features
- **Lazy Loading:** Processes datasets larger than RAM using Python generators.
- **Auto-Validation:** Automatically drops empty or short text records.
- **Observability:** Provides detailed statistical reports on data quality.
- **CLI Interface:** simple command-line usage.

## Installation

```bash
# Clone the repo
git clone [https://github.com/rgb-99/nlp-dataset-engine.git](https://github.com/rgb-99/nlp-dataset-engine.git)

# Install in editable mode
cd nlp-dataset-engine
pip install -e .[dev]
```

## Usage

### 1. Ingest Data (CSV → JSONL)
Convert massive raw CSV files into clean, validated JSONL datasets for AI training. This runs in O(1) memory.

```bash
# Basic usage
nlp-engine ingest --input raw_data.csv --output clean_dataset.jsonl --col text
```
### 2. Automatic Observability & Filtering
The engine automatically enforces data quality:
* **Language Detection:** Removes non-English text by default.
* **Health Report:** Prints a statistical summary (drop rate, speed, count) after every run.
* **Noise Filtering:** Rejects rows where >30% of characters are symbols or numbers (e.g., "### 12345").
**Disable English Filtering:**
If you want to keep all languages (e.g., for a multilingual dataset), use the `--no-english` flag:

```bash
nlp-engine ingest --input global_data.csv --output clean.jsonl --no-english
```
### 3. Recursive Folder Ingestion
Process an entire directory of data files (CSVs and TXTs) at once. The engine will find all compatible files in subfolders, process them, and aggregate the statistics.

```bash
# Ingest entire folder recursively
nlp-engine ingest --input ./data/raw_dump/ --output ./data/clean_combined.jsonl
```
### 4. Advanced Production Features (Big Data)
For massive datasets (Terabytes), use these flags to manage resources and failures.

**Sharding:** Automatically split output into smaller chunks (e.g., 10k rows per file).
```bash
nlp-engine ingest --input ./data --output clean.jsonl --shard-size 10000
# Output: clean-0000.jsonl, clean-0001.jsonl...
```
### 5. Data Integrity & Compression
Ensure your dataset is safe, verifiable, and compact.

**Compression:** Use `--compress` to save disk space (GZIP).
```bash
nlp-engine ingest --input ./data --output final.jsonl --compress
# Output: final-0000.jsonl.gz, final-0001.jsonl.gz...
```
### 6. Benchmarking
Measure the raw throughput (rows/second) of your environment.
This runs the pipeline without writing to disk to test CPU/Validation speed.

```bash
nlp-engine benchmark --input large_dataset.csv
# Output:
#  BENCHMARK RESULTS
#  Rows/Sec: 12500.0
#  MB/Sec:   15.2 MB/s
# BENCHMARK RESULTS
# Rows/Sec: 12500.0
