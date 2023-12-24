"""
LOL - a bit underwhelming in the case of CLI output but using the same approach across all display types.
Not overkill in the other cases.
"""
import logging
from pathlib import Path

def display(formatted_help: str, **_kwargs):
    print(formatted_help)
