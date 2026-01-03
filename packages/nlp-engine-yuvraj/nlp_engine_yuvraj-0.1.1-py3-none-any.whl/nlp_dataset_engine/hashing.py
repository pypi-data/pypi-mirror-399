import hashlib

def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """
    Calculates the SHA256 hash of a file by reading it in chunks.
    This is memory efficient for large files.
    """
    sha256 = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
            
    return sha256.hexdigest()