import hashlib

from models.file_repository import FileRepository
from models.helpers.file_extensions import FileExtensions

class FileController:
    def __init__(self) -> None:
        self.file_repo = FileRepository()
        self.duplicate_files = []

    def scan_directory(self, directory):
        file_list = FileExtensions.getAll(directory)
        self.duplicate_files = self.find_duplicate_files(file_list)

    async def scan_directory_async(self, directory, progress_callback):
        file_list = FileExtensions.getAll(directory)

        total_files = len(file_list)
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
    
        # for index, file_path in enumerate(file_list, 1):
        #     if index % 10 == 0:  # Update progress for every 10 files processed
        #         progress += progress_step * 10
        #         await progress_callback(progress)

        #     dupes = await self.find_duplicate_files(file_list)
        #     if len(dupes) > 0:
        #         dupe_list.append(dupes)

        if progress < 100:
            await progress_callback(100)
        #progress_callback(100) #complete the progress
        self.duplicate_files = duplicate_files #self.find_duplicate_files(file_list)


    async def find_duplicate_files(self, files):
        # Group files by their size
        # size_groups = {}
        # for file_path in files:
        #     size = os.path.getsize(file_path)
        #     if size in size_groups:
        #         size_groups[size].append(file_path)
        #     else:
        #         size_groups[size] = [file_path]

        # Compare files within each hash for duplicates
        duplicate_files = []
        hash_groups = {}
        for file_path in files:
            with open(file_path, "rb") as file:
                file_hash = hashlib.md5(file.read()).hexdigest()
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = [file_path]
                else:
                    hash_groups[file_hash].append(file_path)

        duplicate_files = [group for group in hash_groups.values() if len(group) > 1]
        return duplicate_files