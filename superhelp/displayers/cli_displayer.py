"""
LOL - a bit underwhelming in the case of CLI output but using the same approach across all display types.
Not overkill in the other cases.
"""
import logging
from pathlib import Path

def display(formatted_help: str, file_path: Path):
    logging.info("Ignoring file_path arg in CLI context")
    print(formatted_help)
