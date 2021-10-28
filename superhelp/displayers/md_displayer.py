"""
LOL - a bit underwhelming in the case of CLI output.
"""
from pathlib import Path

from superhelp import gen_utils

def display(formatted_help: str, file_path: Path):
    if file_path:
        raw_file_name = gen_utils.clean_path_name(file_path)
        file_name = f'{raw_file_name}.md'
    else:
        file_name = 'superhelp.md'
    with gen_utils.make_open_tmp_file(file_name, mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        tmp_fh.write(formatted_help)
    print(formatted_help)
    print(f"""\
    {'-' * 10} Content above this line saved as temp file {'-' * 10}
    Temp file: {fpath}
    """)
