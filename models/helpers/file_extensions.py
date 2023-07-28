import os
import hashlib

from models.constants import CONSTANTS

class FileExtensions:

    # get all files recursively
    def getAll(directory):
        try:
            file_list = []
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not any(file_path.lower().endswith(ext) for ext in CONSTANTS.EXCLUDE_FILE_EXT):
                        file_list.append(file_path)
            return file_list
        except:
            return None

    
    # Calculates the MD5 hash of a file
    def getFileHash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def delete_file(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False