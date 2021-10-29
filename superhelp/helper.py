import argparse
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Generator, NamedTuple

from superhelp import conf, gen_utils, helpers, messages
from superhelp.conf import Format, Level, Theme
from superhelp.formatters import cli_formatter, html_formatter, md_formatter
from superhelp.displayers import cli_displayer, html_displayer, md_displayer

logging.basicConfig(
    level=conf.LOG_LEVEL,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

helpers.load_helpers()

class OutputSettings(NamedTuple):
    format_name: Format  ## name of displayer e.g. html
    theme_name: Theme  ## theme name e.g. dark
    detail_level: Level  ## level of detail e.g. Extra
    warnings_only: bool = False  ## show warnings only
    execute_code: bool = False  ## execute code (vs only relying on inspection of AST)


class Pipeline:
    """
    The parts of the pipeline from source inputs to either
    formatted help content or displayed help content.
    """
    FORMAT2FORMATTER_MOD = {
        Format.HTML: html_formatter,
        Format.CLI: cli_formatter,
        Format.MD: md_formatter}
    FORMAT2DISPLAYER_MOD = {
        Format.HTML: html_displayer,
        Format.CLI: cli_displayer,
        Format.MD: md_displayer}
    @staticmethod
    def _get_file_paths(
            project_path: Path, exclude_folders: list[Path]) -> list[Path]:
        """
        Very easy to end up with far too many modules to process e.g. if
        inadvertently looking at every module inside the site packages in a
        virtual env ;-).
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

    @staticmethod
    def _neutralise_superhelp_import_in_code(code: str) -> str:
        ## prevent infinite recursion where superhelp executes script calling superhelp which in turn would etc etc
        code = (code  ## only fixing simple cases - if people try harder they _will_ be able to break everything ;-)
            .replace('import superhelp', '# import superhelp')
            .replace('\nsuperhelp.this(', '\n# superhelp.this(')
            .replace('from superhelp import this', '# from superhelp import this')
            .replace('\nthis(', '\n# this(')
        )
        return code

    @staticmethod
    def _get_file_code(file_path: Path) -> str:
        with open(file_path) as f:
            code = f.read()
        code = code.strip('\n')
        code = Pipeline._neutralise_superhelp_import_in_code(code)
        return code

    @staticmethod
    def get_code_items(*,
            code: str = None, file_path: Path = None,
            project_path: Path = None, exclude_folders=None) -> Generator:
        """
        The start of the pipeline.

        Return a generator (often yielding only details for one code item).
        """
        if code:
            code = code.strip('\n')
            file_path = None
            yield code, file_path
        elif file_path:
            code = Pipeline._get_file_code(file_path)
            yield code, file_path
        elif project_path:
            file_paths = Pipeline._get_file_paths(project_path, exclude_folders)
            for file_path in file_paths:
                code = Pipeline._get_file_code(file_path)
                yield code, file_path
        else:
            code = conf.TEST_SNIPPET
            logging.info("Using default snippet because no code provided")
            file_path = None
            yield code, file_path

    @staticmethod
    def get_code_items_dets(
            code_items: Generator, *, output_settings: OutputSettings) -> Generator:
        """
        Second part of pipeline - code items to code item details.
        """
        repeat_set = set()  ## mutates as we hand it around to keep track of repeats
        for code, file_path in code_items:
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
                        repeat_set=repeat_set)
                except Exception as e:
                    messages_dets = messages.get_error_messages_dets(e, code)
                    multi_block = False
            yield code, file_path, messages_dets, multi_block

    @staticmethod
    def _get_formatter_module(format_name: Format) -> ModuleType:
        try:
            formatter_module = Pipeline.FORMAT2FORMATTER_MOD[format_name]
        except KeyError:
            raise ValueError(f"A format was supplied that lacks a formatter module")
        else:
            return formatter_module

    @staticmethod
    def _get_displayer_module(format_name: Format) -> ModuleType:
        try:
            displayer_module = Pipeline.FORMAT2DISPLAYER_MOD[format_name]
        except KeyError:
            raise ValueError(f"A format ({format_name}) was supplied "
                "that lacks a displayer module")
        else:
            return displayer_module

    @staticmethod
    def get_formatted_help_dets(code_items_dets: Generator,
            output_settings: OutputSettings, in_notebook=False) -> Generator:
        """
        Third part of pipeline - from code item details to formatted content.
        """
        formatter_module = Pipeline._get_formatter_module(
            output_settings.format_name)
        for code, file_path, messages_dets, multi_block in code_items_dets:
            kwargs = {
                'code': code, 'file_path': file_path,
                'messages_dets': messages_dets,
                'detail_level': output_settings.detail_level,
                'warnings_only': output_settings.warnings_only,
                'multi_block': multi_block,
            }
            format_name = output_settings.format_name
            if format_name == Format.HTML:
                kwargs['in_notebook'] = in_notebook
            elif format_name == Format.CLI:
                kwargs['theme_name'] = output_settings.theme_name
            elif format_name == Format.MD:
                pass  ## nothing to add
            else:
                raise ValueError(f"Unexpected format_name {format_name} "
                    "when setting formatter args")
            formatted_help = formatter_module.get_formatted_help(**kwargs)
            yield formatted_help, file_path

    @staticmethod
    def display_help(formatted_help_dets: Generator, format_name: Format, *,
            single_script=True):
        """
        Final stage of the pipeline.

        If HTML will open a tab per script.
        If interactive, will open one after the other
        with a user-controlled pause in between.
        """
        displayer_module = Pipeline._get_displayer_module(format_name)
        for formatted_help, file_path in formatted_help_dets:
            displayer_module.display(formatted_help, file_path)
            if not single_script and format_name in Format.INTERACTIVE_FORMATS:
                input("Press any key to continue ...")


def get_formatted_help_dets(code=None, *,
        file_path=None, project_path=None, exclude_folders=None,
        output_settings: OutputSettings = None, in_notebook=False):
    """
    Get formatted help text. Not displayed by SuperHELP.
    Any display is the responsibility of the calling code.

    If a snippet of code supplied, get help for that. If not, try file_path and
    use that instead. And if not that, try project_path. Finally use the default
    snippet.

    :param str code: (optional) snippet of valid Python code to get help for.
     If None will try the file_path, then the project_path, and finally the
     default snippet.
    :param str file_path: (optional) file path containing Python code
    :param str project_path: (optional) path to project containing Python code
    :param list exclude_folders: may be crucial if setting project_path e.g. to
     avoid processing all python scripts in a virtual environment folder
    :param OutputSettings output_settings:
    :param bool in_notebook: if True changes the formatting to make it
     Jupyter notebook friendly (default False)
    """
    code_items = Pipeline.get_code_items(code=code, file_path=file_path,
        project_path=project_path, exclude_folders=exclude_folders)
    code_items_dets = Pipeline.get_code_items_dets(
        code_items, output_settings=output_settings)
    formatted_help_dets = Pipeline.get_formatted_help_dets(
        code_items_dets, output_settings=output_settings,
        in_notebook=in_notebook)
    return formatted_help_dets
    
def show_help(code=None, *,
        file_path=None, project_path=None, exclude_folders=None,
        output_settings: OutputSettings = None, in_notebook=False):
    """
    If a snippet of code supplied, get help for that. If not, try file_path and
    use that instead. And if not that, try project_path. Finally use the default
    snippet.

    :param str code: (optional) snippet of valid Python code to get help for.
     If None will try the file_path, then the project_path, and finally the
     default snippet.
    :param str file_path: (optional) file path containing Python code
    :param str project_path: (optional) path to project containing Python code
    :param list exclude_folders: may be crucial if setting project_path e.g. to
     avoid processing all python scripts in a virtual environment folder
    :param OutputSettings output_settings:
    :param bool in_notebook: if True changes the formatting to make it
     Jupyter notebook friendly (default False)
    """
    formatted_help_dets = get_formatted_help_dets(code=code,
        file_path=file_path,
        project_path=project_path, exclude_folders=exclude_folders,
        output_settings=output_settings, in_notebook=in_notebook)
    if conf.SHOW_OUTPUT:
        single_script = project_path is None
        Pipeline.display_help(formatted_help_dets, output_settings.format_name,
            single_script=single_script)
    else:
        logging.info("NOT showing output because conf.SHOW_OUTPUT is False "
            "- presumably running tests "
            "and not wanting lots of HTML windows opening ;-)")

def this(*, file_path=None,
        output=Format.HTML, theme_name=Theme.DARK,
        detail_level=Level.EXTRA,
        warnings_only=False, execute_code=False):
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
     (default False)
    """
    if not file_path:
        file_path = gen_utils.get_introspected_file_path()
    output_settings = OutputSettings(
        format_name=output, theme_name=theme_name, detail_level=detail_level,
        warnings_only=warnings_only, execute_code=execute_code)
    show_help(code=None, file_path=file_path, project_path=None,
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
        required=False,
        choices=Level.OPTIONS, default=Level.EXTRA,
        help="What level of detail do you want?")
    parser.add_argument('-o', '--output', type=str,
        required=False,
        choices=Format.OPTIONS, default=default_output,
        help="How do you want your help shown? html, cli, md, etc")
    ## https://docs.python.org/3.10/library/argparse.html#action-classes 'store_true' and 'store_false' - These are special cases of 'store_const' used for storing the values True and False respectively. In addition, they create default values of False and True respectively.
    parser.add_argument('-w', '--warnings-only', action='store_true',
        default=False,
        help="Show warnings only")
    parser.add_argument('-x', '--execute-code', action='store_true',
        default=False,
        help="Execute script to enable additional checks")
    parser.add_argument('-t', '--theme', type=str,
        required=False,
        choices=Theme.OPTIONS, default=Theme.DARK,
        help=("Select an output theme - currently only affects cli output "
            f"option. '{conf.Theme.DARK}' or '{conf.Theme.LIGHT}'"))
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
    output_settings = OutputSettings(format_name=output,
        theme_name=args.theme, detail_level=args.detail_level,
        warnings_only=args.warnings_only, execute_code=args.execute_code)
    show_help(args.code,
        file_path=args.file_path,
        project_path=args.project_path, exclude_folders=args.exclude_folders,
        output_settings=output_settings, in_notebook=False
    )

if __name__ == '__main__':
    # output_settings = OutputSettings(
    #     format_name=Format.HTML if conf.SHOW_OUTPUT else None,
    #     theme_name=None, detail_level=Level.EXTRA,
    #     warnings_only=False, execute_code=False)
    # show_help(output_settings=output_settings)
    # output_settings = OutputSettings(
    #     format_name=Format.CLI if conf.SHOW_OUTPUT else None,
    #     theme_name=Theme.DARK, detail_level=Level.EXTRA,
    #     warnings_only=False, execute_code=False)
    # show_help(output_settings=output_settings)
    # output_settings = OutputSettings(
    #     format_name=Format.MD if conf.SHOW_OUTPUT else None,
    #     theme_name=None, detail_level=Level.EXTRA,
    #     warnings_only=False, execute_code=False)
    # show_help(output_settings=output_settings)
    shelp()
