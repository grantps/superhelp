import argparse
import inspect
import logging

try:
    from .. import conf  # @UnresolvedImport @UnusedImport
    ## importing from superhelp only works properly after I've installed superhelp as a pip package (albeit as a link to this code using python3 -m pip install --user -e <path_to_proj_folder>)
    ## Using this as a library etc works with . instead of superhelp but I want to be be able to run the helper module from within my IDE
    from . import advisors, messages  # @UnusedImport
    from .displayers import cli_displayer, html_displayer, md_displayer  # @UnusedImport
except (ImportError, ValueError):
    from pathlib import Path
    import sys
    parent = str(Path.cwd().parent)
    sys.path.insert(0, parent)
    from superhelp import conf, advisors, messages  # @Reimport
    from superhelp.displayers import cli_displayer, html_displayer, md_displayer  # @Reimport

logging.basicConfig(
    level=conf.LOG_LEVEL,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

advisors.load_advisors()

def display_messages(displayer, snippet, messages_dets, *,
        detail_level=conf.BRIEF,
        warnings_only=False, in_notebook=False, multi_block=False):
    res = displayer.display(snippet, messages_dets,
        detail_level=detail_level,
        warnings_only=warnings_only, in_notebook=in_notebook,
        multi_block=multi_block)
    if in_notebook:
        return res

def _get_snippet(snippet, file_path):
    if snippet and file_path:
        raise Exception("Either set code or file-path, not both")
    elif file_path:
        with open(file_path) as f:
            snippet = f.read()
    elif snippet:
        pass
    else:
        snippet = conf.TEST_SNIPPET
        logging.info("Using default snippet because no snippet provided")
    snippet = snippet.strip('\n')
    ## prevent infinite recursion where superhelp executes script calling superhelp which in turn would etc etc
    snippet = (snippet  ## only fixing simple cases - if people try harder they _will_ be able to break everything ;-)
        .replace('import superhelp', '# import superhelp')
        .replace('\nsuperhelp.this(', '\n# superhelp.this(')
        .replace('from superhelp import this', '# from superhelp import this')
        .replace('\nthis(', '\n# this(')
    )
    return snippet

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

def get_help(snippet=None, *, file_path=None,
        output='html', detail_level=conf.EXTRA,
        warnings_only=False, in_notebook=False):
    """
    Provide advice about the snippet of Python code supplied

    :param str snippet: (optional) snippet of valid Python code to get help for.
     If None will try the file_path and if that is None will use the default
     snippet.
    :param str file_path: (optional) file path containing Python code
    :param str output: type of output e.g. 'html', 'cli', 'md'. Defaults to
     'html'.
    :param str detail_level: e.g. 'Brief', 'Main', 'Extra'
    :param bool warnings_only: if True only displays warnings
    :param bool in_notebook: if True might change way display happens e.g. HTML
     not sent to browser but returned for display by notebook itself
    """
    snippet = _get_snippet(snippet, file_path)
    if snippet.strip() == 'import community':
        messages_dets = messages.get_community_message(snippet)
        multi_block = False
    elif all([word in snippet for word in conf.XKCD_WARNING_WORDS]):
        messages_dets = messages.get_xkcd_warning(snippet)
        multi_block = False
    else:
        try:
            messages_dets, multi_block = messages.get_snippet_dets(
                snippet, warnings_only=warnings_only)
        except Exception as e:
            messages_dets = messages.get_error_messages_dets(e, snippet)
            multi_block = False
    displayer_module = _get_displayer_module(output)
    if displayer_module:
        res = display_messages(displayer_module, snippet,
            messages_dets, detail_level=detail_level,
            warnings_only=warnings_only, in_notebook=in_notebook,
            multi_block=multi_block)
        if in_notebook:
            return res

def _get_introspected_file_path():
    """
    The actual call we are interested in isn't necessarily the second one (e.g.
    console first then actual script) so we have to explicitly filter for it. In
    pydev, for example, it was the third item.

    https://stackoverflow.com/questions/13699283/how-to-get-the-callers-filename-method-name-in-python
    wasn't correct but gave some hints that I could build upon
    """
    for item in inspect.stack():
        has_superhelp_this = (
            item.code_context is not None
            and 'superhelp.this' in ''.join(item.code_context))  ## seems to be a list of one item in each case
        if has_superhelp_this:
            calling_item = item
            break
    else:  ## didn't break for-loop
        raise Exception('Unable to identify calling script through '
            "introspection. Did you rename 'superhelp' or 'this'? "
            "If that isn't the problem try explicitly supplying "
            "file_path e.g. superhelp.this(file_path=__file__)'")
    file_path = calling_item.filename
    return file_path

def this(*, output='html', detail_level=conf.EXTRA,
        warnings_only=False, file_path=None):
    """
    Get SuperHELP output on the file_path Python script.

    Yes - this messes up the ability to "import this" later because I've shaded
    the name "this" in this namespace by naming this function, err ..., "this".
    But it was considered of paramount importance to give users a simple and
    easy-to-remember superhelp.this() interface.

    :param str output: type of output e.g. 'html', 'cli', 'md'. Defaults to
     'html'.
    :param str detail_level: e.g. 'Brief', 'Main', 'Extra'
    :param bool warnings_only: if True only displays warnings
    :param str / Path file_path: full path to script location. Only needed if
     SuperHELP is unable to locate the script by itself. Usually should be
     __file__ (note the double underscores on either side of file).
    """
    if not file_path:
        file_path = _get_introspected_file_path()
    get_help(snippet=None, file_path=file_path,
        output=output, detail_level=detail_level,
        warnings_only=warnings_only, in_notebook=False)

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
            "Either supply the code here or via --file-path (-f)"))
    parser.add_argument('-f', '--file-path', type=str,
        required=False,
        help=("File location of a line, snippet, or script of Python code. "
            "Either point to the code here or supply it using --code (-c)"))
    parser.add_argument('-d', '--detail-level', type=str,
        required=False, default='Extra',
        help="What level of detail do you want? Brief, Main, or Extra?")
    parser.add_argument('-o', '--output', type=str,
        required=False, default=default_output,
        help="How do you want your help shown? html, cli, md, etc")
    parser.add_argument('-w', '--warnings-only', action='store_true',
        default=False,
        help="Show warnings only")
    parser.add_argument('-a', '--advice-list', action='store_true',
        default=False,
        help="List available advice")
    args = parser.parse_args()
    if args.advice_list:
        print("\n======================================")
        print("Specific help available from SuperHELP")
        print("======================================\n")
        advisor_comments = advisors.get_advisor_comments()
        num_width = len(str(len(advisor_comments)))
        for n, (comment, source, warning) in enumerate(
                advisor_comments, 1):
            print(f"{n:>{num_width}}) {warning}{comment} ({source})")
        return
    if args.output and args.file_path:
        print(
            "Either supply code using -c / --code "
            "(usually for smaller snippets of Python) "
            "OR refer to a file of Python code using -f / --file-path")
        return
    output = args.output if conf.SHOW_OUTPUT else None
    get_help(args.code, file_path=args.file_path,
        output=output, detail_level=args.detail_level,
        warnings_only=args.warnings_only, in_notebook=False)

if __name__ == '__main__':
    get_help(file_path='store/get_verse.py')
#     shelp()
