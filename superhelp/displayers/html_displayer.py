from pathlib import Path
import webbrowser

from superhelp import conf, gen_utils

def display(formatted_help: str, *, code_file_path: Path, tmp_html_path: Path | None = None, **_kwargs):
    """
    Show for overall snippet and then by code blocks as appropriate.
    If there are multiple output files (because we are getting help on multiple scripts) will be called multiple times.
    """
    if code_file_path:
        raw_file_name = gen_utils.clean_path_name(code_file_path)
        output_file_name = f'{raw_file_name}.html'
    else:
        output_file_name = 'superhelp_output.html'
    if tmp_html_path:  ## blame snap packaged web browser sand-boxing for this ;-)
        superhelp_tmpdir = tmp_html_path
    else:
        superhelp_tmpdir = gen_utils.get_superhelp_tmpdir(folder=conf.SUPERHELP_PROJECT_OUTPUT)
    with gen_utils.make_open_tmp_file(output_file_name, superhelp_tmpdir=superhelp_tmpdir, mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        tmp_fh.write(formatted_help)
    url = fpath.as_uri()
    webbrowser.open_new_tab(url)
