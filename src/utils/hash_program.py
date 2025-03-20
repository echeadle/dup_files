import os
import hashlib


def create_hash(folder_path):
    hashes = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                hash = hashlib.md5(f.read())
                hashes[file_path] = hash.hexdigest()
    return hashes


folder_path = "/path/to/folder"
hashes = create_hash(folder_path)

print(hashes)
