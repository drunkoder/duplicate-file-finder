class File:
    def __init__(self, file_type, name, size, num_of_files, last_modified, file_hash, parent_id=None) -> None:
        self.file_type = file_type
        self.name = name
        self.size = size
        self.num_of_files = num_of_files
        self.last_modified = last_modified
        self.file_hash = file_hash
        self.parent_id = parent_id
