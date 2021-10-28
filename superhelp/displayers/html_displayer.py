from pathlib import Path
import webbrowser

from superhelp import conf, gen_utils

def display(formatted_help: str, file_path: Path):
    """
    Show for overall snippet and then by code blocks as appropriate.
    """
    if file_path:
        raw_file_name = gen_utils.clean_path_name(file_path)
        file_name = f'{raw_file_name}.html'
    else:
        file_name = 'superhelp_output.html'
    superhelp_tmpdir = gen_utils.get_superhelp_tmpdir(
        folder=conf.SUPERHELP_PROJECT_OUTPUT)
    with gen_utils.make_open_tmp_file(
            file_name, superhelp_tmpdir=superhelp_tmpdir,
            mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        tmp_fh.write(formatted_help)
    url = fpath.as_uri()
    webbrowser.open_new_tab(url)
