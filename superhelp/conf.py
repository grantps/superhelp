import datetime
import logging

t = True
f = False

## =============================================================================

## Release settings in (). Enforced by Makefile using good old sed :-)

c = 'cli'
h = 'html'
m = 'md'

RECORD_AST = f  ## (f)
OUTPUT = h  ## set html as default output (h)
SHOW_OUTPUT = t  ## f is only ever used when testing pre-display (t)
INCLUDE_LINTING = t  ## f when running unit tests to massively speed them up (otherwise every snippet in tests is linted each time) (t)
LOG_LEVEL = logging.INFO  ## (logging.INFO)
## =============================================================================

## When testing user-supplied snippets watch out for the BOM MS inserts via Notepad. AST chokes on it.
## All snippets here should be raw strings (see https://stackoverflow.com/questions/53636723/python-parsing-code-with-new-line-character-in-them-using-ast)
TEST_SNIPPET = r"""
details = [(1, 2), ]
a, b = details[0]
"""

PY3_6 = '3.6'
PY3_7 = '3.7'
PY3_8 = '3.8'

LINUX = 'linux'
WINDOWS = 'windows'
MAC = 'mac'

AST_OUTPUT_XML_FNAME = 'ast_output.xml'

PYTHON_CODE_START = '__python_code_start__'
PYTHON_CODE_END = '__python_code_end__'

MD_PYTHON_CODE_START = '::python'

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
DETAIL_LEVELS = [BRIEF, MAIN, EXTRA]

ANON_NAME = 'Anonymous'

INT_TYPE = 'int'
FLOAT_TYPE = 'float'
STR_TYPE = 'str'
DATETIME_TYPE = 'datetime'
BOOLEAN_TYPE = 'bool'
LIST_TYPE = 'list'
DICT_TYPE = 'dict'
TUPLE_TYPE = 'tuple'

TYPE2NAME = {
    INT_TYPE: 'integer',
    FLOAT_TYPE: 'float',
    STR_TYPE: 'string',
    DATETIME_TYPE: 'datetime object',
    BOOLEAN_TYPE: 'boolean',
    LIST_TYPE: 'list',
    DICT_TYPE: 'dict',
    TUPLE_TYPE: 'tuple',
}

EXAMPLES_OF_TYPES = {  ## best to include at least three so we have enough to append one and from what is left extend multiple
    INT_TYPE: [123, 9, 17, 20, 100, 2020, 16],
    FLOAT_TYPE: [1.2345, 0.667, 0.1, 0.001, 10.0],
    STR_TYPE: ['apple', 'banana', 'kiwifruit', 'Auckland, New Zealand'],
    DATETIME_TYPE: [
        datetime.date(2020, 4, 4),
        datetime.date(1066, 10, 14),
        datetime.datetime.today(), ],
    BOOLEAN_TYPE: [True, False],
    LIST_TYPE: [[10, 2], [-3, 20], [44, -180]],
    DICT_TYPE: [{'x': 10, 'y': 2}, {'x': -3, 'y': 20}, {'x': 44, 'y': -180}],
    TUPLE_TYPE: [(10, 2), (-3, 20), (44, -180)],
}

STD_NAME = 'std_name'
DICT_KEY_NAME = 'dict_key_name'
OBJ_ATTR_NAME = 'obj_attr_name'

MAX_BRIEF_FUNC_LOC = 35
MAX_BRIEF_FUNC_ARGS = 6
MIN_BRIEF_DOCSTRING = 3
MIN_BRIEF_NAME = 3
MAX_BRIEF_NESTED_BLOCK = 20
MIN4ANY_OR_ALL = 3
MAX_ITEMS_EVALUATED = 25

FUNCTION_LBL = 'function'
METHOD_LBL = 'method'

EMAIL2USE = 'superhelp@p-s.co.nz'

WARNINGS_ONLY_MSG = ("Only displaying warnings. "
    "To see all help, set warnings only option to False")
ALL_HELP_SHOWING_MSG = ("Displaying all help. "
    "To only see warnings, set warnings only option to True")

INTRO = ("Help is provided for your overall snippet and for each block of code "
    "as appropriate. If there is nothing to say about a block it is skipped.")
NO_ADVICE_MESSAGE = ("No advice to give - looks fine :-). But if you think "
    f"there should have been some advice given, contact {EMAIL2USE} "
    "with the subject line 'Advice' and explain. Please include a snippet to "
    "test as well.")
MISSING_ADVICE_MESSAGE = ("If there was some advice you think should have "
    f"been given that wasn't, contact {EMAIL2USE} with the subject line "
    "'Advice' and explain. Please include a snippet to test as well.")
SYSTEM_MESSAGE = 'System message'

## input types
BLOCKS_DETS = 'blocks_dets'
SNIPPET_STR = 'snippet_str'

XKCD_WARNING_WORDS = ['supervolcano', 'seagull', 'garbage disposal']

VERBOSE_FLAG = 'VERBOSE'
INLINE_RE_VERBOSE_FLAG = '(?x)'

SNIPPET_FNAME = 'snippet.py'
LINT_MSG_TYPE = 'msg_type'
LINT_MSG = 'msg'
LINT_LINE_NO = 'line_no'

LINE_FEED = '&#10;'

## scraped from https://docs.python.org/3/py-modindex.html 2020-04-02
STD_LIBS = ['__future__', '__main__', '_dummy_thread', '_thread', 'aifc',
'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit',
'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2',
'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop',
'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
'dis', 'distutils', 'doctest', 'dummy_threading', 'email', 'encodings',
'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput',
'fnmatch', 'formatter', 'fractions', 'ftplib', 'functools', 'gc', 'getopt',
'getpass', 'gettext', 'glob', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html',
'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress',
'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging',
'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap',
'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis',
'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser',
'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform',
'plistlib', 'poplib', 'posix', 'pprint', 'profile', 'pstats', 'pty', 'pwd',
'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline',
'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select',
'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib',
'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'ssl', 'stat',
'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol',
'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib',
'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit',
'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty',
'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib',
'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg',
'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile',
'zipimport', 'zlib']
