import os
import hashlib
import shutil

from models.constants import CONSTANTS

class FileService:

    def __init__(self):
        pass

    # get all files recursively
    def get_all(self, directory):
        try:
            file_list = []
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file) #.replace('/', '\\')
                    if not any(file_path.lower().endswith(ext) for ext in CONSTANTS.EXCLUDE_FILE_EXT):
                        file_list.append(file_path)
            return file_list
        except:
            return None

    
    # Calculates the MD5 hash of a file
    def get_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print("An error occurred:", e)
        
    def delete_all_in_directory(self, directory_path):
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")

            print("All contents inside the directory have been deleted.")
            return True
        except Exception as e:
            print("An error occurred:", e)
            return False

    def open_directory(self, directory_path):
        try:
            os.startfile(directory_path) # Opens the directory in File Explorer
        except Exception as e:
            print("An error occurred:", e)


    def move_file_to_directory(self, source, destination_directory):
        try:
            if not os.path.exists(source):
                print("Source file does not exist.")
                return False
        
            source_file_name = os.path.basename(source)
            destination = os.path.join(destination_directory, source_file_name)
            if os.path.exists(destination):
                file_name, file_extension = os.path.splitext(os.path.basename(destination))
                counter = 1
                while os.path.exists(destination):
                    new_file_name = f"{file_name}_{counter}{file_extension}"
                    destination = os.path.join(destination_directory, new_file_name)
                    counter += 1

            shutil.move(source, destination)
            print("File moved successfully.")
            return True
        except Exception as e:
            print("An error occurred:", e)
            return False
        
    def get_staging_directory(self):
        with open(CONSTANTS.STAGING_PATH, 'r') as file:
            return file.read()