import logging
from os import rename
from pathlib import Path
import platform
import sys
import tempfile
from textwrap import dedent, wrap

from . import conf

def get_os_platform():
    platforms = {
        'Linux': conf.LINUX, 'Windows': conf.WINDOWS, 'Darwin': conf.MAC}
    os_platform = platforms.get(platform.system())
    return os_platform

def make_open_tmp_file(fname, mode='w'):
    """
    Note - file needs to be closed for changes to be saved to the file -
    otherwise it will be 0 bytes. Up to client code to ensure it is closed and
    properly available for subsequent steps.
    """
    tmp_fh = tempfile.NamedTemporaryFile(mode=mode, delete=False)
    randomly_named_fpath = Path(tmp_fh.name)
    fpath = Path(randomly_named_fpath.parent) / fname
    rename(randomly_named_fpath, fpath)
    return tmp_fh, fpath

def get_python_version():
    major, minor = sys.version_info[:2]
    return f"{major}.{minor}"

def get_nice_str_list(items, *, quoter='`'):
    """
    Get a nice English phrase listing the items.

    :param sequence items: individual items to put into a phrase.
    :param str quoter: default is backtick because it is expected that the most
     common items will be names (variables).
    :return: nice phrase
    :rtype: str
    """
    nice_str_list = ', '.join(
        [f"{quoter}{item}{quoter}" for item in items[:-1]])
    if nice_str_list:
        nice_str_list += " and "
    nice_str_list += f"{quoter}{items[-1]}{quoter}"
    return nice_str_list

def int2nice(num):
    """
    :return: nicer version of number ready for use in sentences
    :rtype: str
    """
    nice = {
        0: 'no',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
        6: 'six',
        7: 'seven',
        8: 'eight',
        9: 'nine',
        10: 'ten',
        11: 'twelve',
        12: 'twelve',
    }
    return nice.get(num, num)

def layout_comment(raw_comment, *, is_code=False):
    """
    Don't break up long lines which are titles otherwise the subsequent parts
    won't carry appropriate heading-level formatting.
    """
    if '`' in raw_comment and is_code:
        logging.debug("Backtick detected in code which is probably a mistake")
    if is_code:
        lines = (
            [conf.PYTHON_CODE_START]
            + dedent(raw_comment).split('\n')
            + [conf.PYTHON_CODE_END]
        )
        indented_lines = [f"{' ' * 4}{line}" for line in lines]
        comment = f'\n'.join(indented_lines) + '\n'  ## new line at end needed otherwise content of next str (if any) becomes part of code highlighting
        comment = f'\n'.join(indented_lines) + '\n'  ## new line at end needed otherwise content of next str (if any) becomes part of code highlighting
    else:
        raw_paragraphs = dedent(raw_comment).split('\n\n')  ## we only split paragraphs if two new lines
        new_paragraphs = []
        for raw_paragraph in raw_paragraphs:
            ## replace internal new lines only - we need to preserve the outer ones
            n_start_new_lines = (
                len(raw_paragraph) - len(raw_paragraph.lstrip('\n')))
            n_end_new_lines = (
                len(raw_paragraph) - len(raw_paragraph.rstrip('\n')))
            paragraph = raw_paragraph.strip()
            one_line_paragraph = paragraph.replace('\n', ' ')  ## actually continuations of same line so no need to put on separate lines
            if one_line_paragraph.startswith('#'):
                wrapped_paragraph_lines = [one_line_paragraph, ]
            else:
                wrapped_paragraph_lines = wrap(one_line_paragraph)
            new_paragraph = (
                (n_start_new_lines * '\n\n')
                + '\n'.join(wrapped_paragraph_lines)
                + (n_end_new_lines * '\n\n')
            )
            new_paragraphs.append(new_paragraph)
        comment = '\n' + '\n\n'.join(new_paragraphs)
    return comment

def get_docstring_start(docstring):
    docstring_start = (
        docstring.lstrip('\n').split('\n\n')[0].strip().replace('\n    ', ' '))
    return docstring_start
