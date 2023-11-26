from pathlib import Path

from superhelp import gen_utils

def display(formatted_help: str, file_path: Path):
    """
    If there are multiple output files (because we are getting help on multiple scripts) will be called multiple times.
    """
    if file_path:
        raw_file_name = gen_utils.clean_path_name(file_path)
        output_file_name = f'{raw_file_name}.md'
    else:
        output_file_name = 'superhelp.md'
    with gen_utils.make_open_tmp_file(output_file_name, mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        tmp_fh.write(formatted_help)
    print(formatted_help)
    print(f"""\
    {'-' * 10} Content above this line saved as temp file {'-' * 10}
    Temp file: {fpath}
    """)
