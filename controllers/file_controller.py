import hashlib

from models.services.file_service import FileService
from models.services.logging_service import LogService

class FileController:
    def __init__(self) -> None:
        self.file_service = FileService()
        self.log_service = LogService()
        self.duplicate_files = []

    async def scan_directory_async(self, directory, progress_callback):
        file_list = self.file_service.get_all(directory)
        total_files = len(file_list)

        if total_files > 0:
            progress_step = 100 / total_files
            progress = 0

            duplicate_files = []
            hash_groups = {}
            for index, file_path in enumerate(file_list, 1):
                with open(file_path, "rb") as file:
                    file_hash = hashlib.md5(file.read()).hexdigest()
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = [file_path]
                    else:
                        hash_groups[file_hash].append(file_path)

                if index % 10 == 0:  # Update progress for every 10 files processed
                    progress += progress_step * 10
                    await progress_callback(progress)
                    

            duplicate_files = [group for group in hash_groups.values() if len(group) > 1]
            if progress < 100:
                await progress_callback(100)
        
            self.duplicate_files = duplicate_files 

    def get_staging_directory(self):
        return self.file_service.get_staging_directory()
    
    def delete_all_in_directory(self, directory_path):
        return self.file_service.delete_all_in_directory(directory_path)
    
    def delete_file(self, file_path):
        return self.file_service.delete_file(file_path)
    
    def move_file_to_directory(self, source, destination_directory):
        return self.file_service.move_file_to_directory(source, destination_directory)
    
    def open_directory(self, directory_path):
        self.file_service.open_directory(directory_path)
    
    def create_log(self, action, location):
        self.log_service.handle_insert(action, location)
    
    def clear_logs(self):
        return self.log_service.handle_delete()
    
    def get_logs(self):
        return self.log_service.handle_select()