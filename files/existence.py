import os


def file_exists(full_path: str) -> bool:
    return os.path.isfile(full_path)
