import argparse
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
        message_level=conf.BRIEF, in_notebook=False, multi_block=False):
    res = displayer.display(snippet, messages_dets,
        message_level=message_level, in_notebook=in_notebook,
        multi_block=multi_block)
    if in_notebook:
        return res

def _get_snippet(snippet, file_path):
    if snippet and file_path:
        raise Exception("Either set snippet or file-path, not both")
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

def _get_displayer_module(displayer):
    ARG2DISPLAYER = {
        'html': html_displayer,
        'cli': cli_displayer,
        'md': md_displayer,
    }
    displayer_module = ARG2DISPLAYER.get(displayer)
    if displayer_module is None:
        logging.info("Display is currently suppressed - please supply "
            "a displayer if you want advice displayed")
    return displayer_module

def get_advice(snippet=None, *, file_path=None, displayer='html',
        message_level=conf.EXTRA, in_notebook=False):
    """
    Provide advice about the snippet supplied

    :param str snippet: (optional) snippet of valid Python code to provide
     advice on. If None will try the file_path and if that is None will use the
     default snippet
    :param str file_path: (optional) file path containing snippet
    :param str displayer: displayer to use e.g. 'html' or 'cli'. Defaults to
     'html'.
    :param str message_level: e.g. 'Brief', 'Main', 'Extra'
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
            messages_dets, multi_block = messages.get_snippet_dets(snippet)
        except Exception as e:
            messages_dets = messages.get_error_messages_dets(e, snippet)
            multi_block = False
    displayer_module = _get_displayer_module(displayer)
    if displayer_module:
        res = display_messages(displayer_module, snippet, messages_dets,
            message_level=message_level, in_notebook=in_notebook,
            multi_block=multi_block)
        if in_notebook:
            return res

def this(file_path, *, displayer='html', message_level=conf.EXTRA):
    """
    Yes - if you import this later I've wrecked it but it is more important to
    allow superhelp.this() :-).
    """
    get_advice(snippet=None, file_path=file_path, displayer=displayer,
        message_level=message_level, in_notebook=False)

def shelp():
    """
    To get help

    $ shelp -h
    """
    default_displayer = conf.DISPLAYER
    ## don't use type=list ever https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
    parser = argparse.ArgumentParser(
        description='Superhelp - Help for Humans!')
    parser.add_argument('-s', '--snippet', type=str,
        required=False,
        help="Supply a line or brief snippet of Python code")
    parser.add_argument('-f', '--file-path', type=str,
        required=False,
        help="File location of a line or brief snippet of Python code")
    parser.add_argument('-l', '--level', type=str,
        required=False, default='Extra',
        help="What level of help do you want? Brief, Main, or Extra?")
    parser.add_argument('-d', '--displayer', type=str,
        required=False, default=default_displayer,
        help="Where do you want your help shown? html, cli, etc")
    parser.add_argument('-a', '--advice-list', action='store_true',
        default=False,
        help="List available advice")
    args = parser.parse_args()
    if args.advice_list:
        advisor_comments = advisors.get_advisor_comments()
        num_width = len(str(len(advisor_comments)))
        for n, (comment, source) in enumerate(
                advisor_comments, 1):
            print(f"{n:>{num_width}}) {comment} ({source})")
        return
    displayer = args.displayer if conf.DO_DISPLAYER else None
    get_advice(args.snippet,
        file_path=args.file_path, displayer=displayer, message_level=args.level)

if __name__ == '__main__':
    shelp()
