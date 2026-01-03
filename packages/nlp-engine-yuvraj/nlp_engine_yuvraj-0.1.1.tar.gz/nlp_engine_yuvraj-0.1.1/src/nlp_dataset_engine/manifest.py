import json
import os
import glob
import datetime
from typing import List, Dict
from .hashing import calculate_sha256

class ManifestGenerator:
    """
    Scans the output folder and creates a manifest.json
    containing file integrity hashes and metadata.
    """
    def __init__(self, output_prefix: str):
        self.output_prefix = output_prefix
        # Determine the directory and base filename pattern
        self.output_dir = os.path.dirname(os.path.abspath(output_prefix))
        self.base_name = os.path.basename(output_prefix)

    def generate(self, total_records: int):
        manifest_path = os.path.join(self.output_dir, "manifest.json")
        
        # Find all generated shards (jsonl or jsonl.gz)
        # We look for files starting with the prefix in the same directory
        search_pattern = os.path.join(self.output_dir, f"{self.base_name}-*.jsonl*")
        files = sorted(glob.glob(search_pattern))
        
        file_entries = []
        
        print(f"\n🔐 Generating Manifest...")
        
        for file_path in files:
            print(f"   Hashing: {os.path.basename(file_path)}")
            file_hash = calculate_sha256(file_path)
            file_size = os.path.getsize(file_path)
            
            file_entries.append({
                "filename": os.path.basename(file_path),
                "sha256": file_hash,
                "size_bytes": file_size
            })
            
        manifest = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "total_records": total_records,
            "total_files": len(files),
            "files": file_entries
        }
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        print(f"✅ Manifest saved to: {manifest_path}")