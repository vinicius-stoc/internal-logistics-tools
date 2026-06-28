from pathlib import Path
import hashlib


def calculate_file_sha256(file_path):
    path = Path(file_path)
    hash_builder = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hash_builder.update(chunk)

    return hash_builder.hexdigest()


