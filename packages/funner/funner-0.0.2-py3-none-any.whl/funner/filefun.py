"""
Common file operations for everyday use. Python standard stuff is enriched with logger. 
Mostly Exception-safe (ie. not quiting whole app/script if some file is missing, 
making higher logic implementation scripts tehnically less verbose).
Uses always encoding UTF-8.

"""
import os
from pathlib import Path
import contextlib

from loguru import logger


@contextlib.contextmanager
def open_with_missing_dirs(path: str|Path|os.PathLike, access_mode):
    """
    Open "path" for writing, creating any parent directories as needed.
    Similar to mkdir -p dir & edit file // path = dir + file
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, access_mode, encoding='utf-8') as file_handle:
        yield file_handle


def read_content_of_file(file_full_name: str) -> str | None:
    """File reader with error handling. 
    
    Emits warning if file not exists (except for empty string as file name).
    Emits error if file cannot be read.
    """
    if file_full_name == "":
        return None
    if not os.path.exists(file_full_name):
        logger.warning(f"File {file_full_name} don't exists")
        return None
    try:
        with open(file_full_name, 'r', encoding="utf-8") as sf:
            content = sf.read()
        return content
    except Exception as e1:
        logger.error(f"File {file_full_name} cannot be opened, {e1}")
        return None
