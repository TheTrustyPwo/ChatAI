import json
from os import listdir, path
from typing import Tuple, List
from argparse import Namespace


def get_dir_files(dir_path: str, extension_filter: str = None) -> Tuple[List[str], List[str]]:
    """
    Returns files in the specified directory which match the extension filter
    :param dir_path: Path of the directory to retrieve the files from
    :param extension_filter: File extension filter (i.e. '.txt')
    :return: List of files, List of file paths
    """
    files = listdir(path=dir_path)
    if extension_filter:
        files = [file for file in files if file.endswith(extension_filter)]
    filtered_files = [path.join(dir_path, file) for file in files]
    return files, filtered_files
