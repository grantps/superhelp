import argparse
from collections import namedtuple
import logging
import os

## absolute importing needed in any script being run as a script (vs as library import)
from superhelp import conf, gen_utils, helpers, messages
from superhelp.displayers import cli_displayer, html_displayer, md_displayer

logging.basicConfig(
    level=conf.LOG_LEVEL,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

helpers.load_helpers()

RunContext = namedtuple('RunContext', 'in_notebook, multi_script, repeat_set')
RunContext.__doc__ += (
    ". Information on the context in which this code is being inspected.")
RunContext.in_notebook.__doc__ = ("Is this code inspection being run in a "
    "Jupyter notebook? Boolean. If True might change way display happens "
    "e.g. HTML not sent to browser but returned for display by notebook itself")
RunContext.multi_script.__doc__ = (
    "Is this code inspection being run as one of multiple scripts? Boolean.")
RunContext.repeat_set.__doc__ = ("Data on what has already been run so repeated"
    " content can be skipped or handled in a more light-weight way. Set.")

OutputSettings = namedtuple('OutputSettings',
    'displayer, theme_name, detail_level, warnings_only, execute_code')
OutputSettings.displayer.__doc__ = "str - name of displayer e.g. html"
OutputSettings.theme_name.__doc__ = "str - theme name e.g. dark"
OutputSettings.detail_level.__doc__ = "str - level of detail e.g. Extra"
OutputSettings.warnings_only.__doc__ = "bool - show warnings only"
OutputSettings.execute_code.__doc__ = (
    "bool - execute code (vs only relying on inspection of AST")

def _get_displayer_module(output):
    ARG2DISPLAYER = {
        'html': html_displayer,
        'cli': cli_displayer,
        'md': md_displayer,
    }
    displayer_module = ARG2DISPLAYER.get(output)
    if displayer_module is None:
        logging.info("Display is currently suppressed - please supply "
            "a displayer if you want advice displayed")
    return displayer_module

def _run_display(code, *,
        file_path=None, displayer_module=None, messages_dets=None,
        output_settings=None, run_context=None, multi_block=False):
    if not output_settings:
        raise Exception("Expected OutputSettings named tuple")
    if not run_context:
        raise Exception("Expected RunContext named tuple")
    if len(str(file_path)) > conf.MAX_FILE_PATH_IN_HEADING:
        n_chars2_keep = conf.MAX_FILE_PATH_IN_HEADING - 4
        file_path = '...' + str(file_path)[-n_chars2_keep:]
    kwargs = {'multi_script': run_context.multi_script}
    if output_settings.displayer == conf.CLI:
        kwargs.update({'theme_name': output_settings.theme_name})
    elif output_settings.displayer == conf.HTML:
        kwargs.update(
            {'in_notebook': run_context.in_notebook,
             'multi_script': run_context.multi_script})
    else:
        pass
    deferred_display = displayer_module.display(code, file_path,
        messages_dets, detail_level=output_settings.detail_level,
        warnings_only=output_settings.warnings_only, multi_block=multi_block,
        **kwargs)
    return deferred_display

def get_code_help(code, *, file_path=None,
        output_settings=None, run_context=None):
    """
    Whether looking at individual snippets / scripts or multiple project scripts
    everything passes through here for each code 'snippet'.
    """
    if not output_settings:
        raise Exception("Expected an OutputSettings namedtuple")
    if not run_context:
        raise Exception("Expected a RunContext namedtuple")
    if run_context.multi_script and run_context.in_notebook:
        raise Exception("Notebooks should only ever run on snippets not on "
            "multiple scripts")
    if code.strip() == 'import community':
        messages_dets = messages.get_community_message(code)
        multi_block = False
    elif all([word in code for word in conf.XKCD_WARNING_WORDS]):
        messages_dets = messages.get_xkcd_warning(code)
        multi_block = False
    else:
        try:
            messages_dets, multi_block = messages.get_snippet_dets(code,
                warnings_only=output_settings.warnings_only,
                execute_code=output_settings.execute_code,
                repeat_set=run_context.repeat_set)
        except Exception as e:
            messages_dets = messages.get_error_messages_dets(e, code)
            multi_block = False
    displayer_module = _get_displayer_module(output_settings.displayer)
    if displayer_module:
        deferred_display = _run_display(
            code, file_path=file_path,
            displayer_module=displayer_module, messages_dets=messages_dets,
            output_settings=output_settings, run_context=run_context,
            multi_block=multi_block)
    else:
        deferred_display = None
    return deferred_display

def get_script_help(file_path, *,
        output=conf.HTML, detail_level=conf.EXTRA, theme_name=None,
        warnings_only=False, execute_code=True, run_context=None):
    with open(file_path) as f:
        code = f.read()
    code = code.strip('\n')
    ## prevent infinite recursion where superhelp executes script calling superhelp which in turn would etc etc
    code = (code  ## only fixing simple cases - if people try harder they _will_ be able to break everything ;-)
        .replace('import superhelp', '# import superhelp')
        .replace('\nsuperhelp.this(', '\n# superhelp.this(')
        .replace('from superhelp import this', '# from superhelp import this')
        .replace('\nthis(', '\n# this(')
    )
    get_code_help(code, file_path=file_path,
        output=output, theme_name=theme_name, detail_level=detail_level,
        warnings_only=warnings_only, execute_code=execute_code,
        run_context=run_context)

def _get_file_paths(project_path, exclude_folders):
    """
    Very easy to end up with far too many modules to process e.g. if
    inadvertently looking at every module inside the site packages in a virtual
    env ;-).
    """
    file_paths = []
    for root, dirs, files in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        py_files = [os.path.join(root, file)
            for file in files if file.endswith('.py')]
        file_paths.extend(py_files)
    if len(file_paths) > conf.MAX_PROJECT_MODULES:
        raise Exception(
            f"Too many modules to process - {len(file_paths):,}")
    return file_paths

def get_help(code=None, *,
        file_path=None, project_path=None, exclude_folders=None,
        output_settings=None, in_notebook=False):
    """
    If a snippet of code supplied, get help for that. If not, try file_path and
    use that instead. And if not that, try project_path. Finally use the default
    snippet.

    Only getting deferred display from displayers when looking at code snippets.

    :param str code: (optional) snippet of valid Python code to get help for.
     If None will try the file_path, then the project_path, and finally the
     default snippet.
    :param str file_path: (optional) file path containing Python code
    :param str project_path: (optional) path to project containing Python code
    :param list exclude_folders: may be crucial if setting project_path e.g. to
     avoid processing all python scripts in a virtual environment folder
    :param str output_settings: OutputSettings named tuple
    :param bool in_notebook: if True might change way display happens e.g. HTML
     not sent to browser but returned for display by notebook itself
     (default False)
    """
    if not output_settings:
        raise Exception("Expected OutputSettings named tuple")
    repeat_set = set()  ## mutates as we hand it around to keep track of repeats
    if code:
        code = code.strip('\n')
        run_context = RunContext(
            in_notebook=in_notebook, multi_script=False, repeat_set=repeat_set)
        deferred_display = get_code_help(code, file_path=None,
            output_settings=output_settings, run_context=run_context)
        if not deferred_display:
            return
        if (in_notebook and output_settings.displayer == conf.HTML):
            return deferred_display  ## assumed notebook always HTML and we need to pass on the HTML string to the jupyter notebook
        else:
            raise Exception(
                "Only a notebook with html output should use deferred display")
    elif file_path:
        run_context = RunContext(
            in_notebook=in_notebook, multi_script=False, repeat_set=repeat_set)
        get_script_help(file_path,
            output_settings=output_settings, run_context=run_context)
    elif project_path:
        run_context = RunContext(
            in_notebook=in_notebook, multi_script=True, repeat_set=repeat_set)
        file_paths = _get_file_paths(project_path, exclude_folders)
        for file_path in file_paths:
            get_script_help(file_path,
                output_settings=output_settings, run_context=run_context)
        if output_settings.displayer == conf.HTML:
            gen_utils.open_output_folder()
    else:
        code = conf.TEST_SNIPPET
        logging.info("Using default snippet because no code provided")
        run_context = RunContext(
            in_notebook=in_notebook, multi_script=False, repeat_set=repeat_set)
        get_code_help(code, file_path=None,
            output_settings=output_settings, run_context=run_context)

def this(*, file_path=None,
        output=conf.HTML, theme_name=conf.DARK, detail_level=conf.EXTRA,
        warnings_only=False, execute_code=True):
    """
    Get SuperHELP output on the file_path Python script.

    Yes - this messes up the ability to "import this" later because I've shaded
    the name "this" in this namespace by naming this function, err ..., "this".
    But it was considered of paramount importance to give users a simple and
    easy-to-remember superhelp.this() interface.

    :param str / Path file_path: full path to script location. Only needed if
     SuperHELP is unable to locate the script by itself. Usually should be
     __file__ (note the double underscores on either side of file).
    :param str output: type of output e.g. 'html', 'cli', 'md' (default 'html')
    :param str theme_name: currently only needed by the CLIC displayer to handle
     dark and light terminal themes (default 'dark')
    :param str detail_level: e.g. 'Brief', 'Main', 'Extra' (default 'Extra')
    :param bool warnings_only: if True only displays warnings (default False)
    :param bool execute_code: if True executes code to enable extra checks
     (default True)
    """
    if not file_path:
        file_path = gen_utils.get_introspected_file_path()
    output_settings = OutputSettings(
        displayer=output, theme_name=theme_name, detail_level=detail_level,
        warnings_only=warnings_only, execute_code=execute_code)
    get_help(code=None, file_path=file_path, project_path=None,
        output_settings=output_settings, in_notebook=False)

def shelp():
    """
    To get help

    $ shelp -h
    """
    default_output = conf.OUTPUT
    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    parser.add_argument('-c', '--code', type=str,
        required=False,
        help=("Python code - usually only a line or snippet. "
            "An alternative to --file-path and --project-path"))
    parser.add_argument('-f', '--file-path', type=str,
        required=False,
        help=("File location of a line, snippet, or script of Python code. "
            "An alternative to --code and --project-path"))
    parser.add_argument('-p', '--project-path', type=str,
        required=False,
        help=("Project folder containing all the modules you want help on. "
            "An alternative to --code and --file-path"))
    parser.add_argument('-e', '--exclude-folders', type=str,
        nargs='*', help=("If using -p / --project-path you probably need to "
            "exclude modules in storage folders or a virtual env folder "
            "e.g. --exclude store env back_ups misc"))
    parser.add_argument('-d', '--detail-level', type=str,
        required=False, default='Extra',
        help="What level of detail do you want? Brief, Main, or Extra?")
    parser.add_argument('-o', '--output', type=str,
        required=False, default=default_output,
        help="How do you want your help shown? html, cli, md, etc")
    parser.add_argument('-w', '--warnings-only', action='store_true',
        default=False,
        help="Show warnings only")
    parser.add_argument('-x', '--execute-code', action='store_false',
        default=True,
        help="Execute script to enable additional checks")
    parser.add_argument('-t', '--theme', type=str,
        required=False, default=conf.DARK,
        help=("Select an output theme - currently only affects cli output "
            f"option. '{conf.DARK}' or '{conf.LIGHT}'"))
    parser.add_argument('-a', '--advice-list', action='store_true',
        default=False,
        help="List available advice")
    args = parser.parse_args()
    if args.advice_list:
        print("\n======================================")
        print("Specific help available from SuperHELP")
        print("======================================\n")
        helper_comments = helpers.get_helper_comments()
        num_width = len(str(len(helper_comments)))
        for n, (comment, source, warning) in enumerate(helper_comments, 1):
            print(f"{n:>{num_width}}) {warning}{comment} ({source})")
        return
    sources = [
        src for src in (args.code, args.file_path, args.project_path) if src]
    if len(sources) > 1:
        print(
            "The code you want help on can only be identified in one way. "
            "Either supply code by:"
            "\n1) supplying it directly using -c / --code "
            "(usually for smaller snippets of Python)"
            "\n2) or by referring to a Python script using -f / --file-path "
            "\n3) or by referring to a folder of Python modules using "
            "-p / --project-path"
        )
        return
    logging.debug(args)
    output = args.output if conf.SHOW_OUTPUT else None
    output_settings = OutputSettings(
        displayer=output, theme_name=args.theme, detail_level=args.detail_level,
        warnings_only=args.warnings_only, execute_code=args.execute_code)
    get_help(args.code,
        file_path=args.file_path,
        project_path=args.project_path, exclude_folders=args.exclude_folders,
        output_settings=output_settings, in_notebook=False
    )

if __name__ == '__main__':
#     output_settings = OutputSettings(
#         displayer='html'if conf.SHOW_OUTPUT else None,
#         theme_name=None, detail_level='Extra',
#         warnings_only=False, execute_code=False)
#     get_help(output_settings=output_settings)
    shelp()
