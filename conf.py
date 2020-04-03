from collections import namedtuple
import datetime

LineCodeDets = namedtuple(
    'LineCodeDets', 'element, line_code_str, first_line_no')

MessageDets = namedtuple('MessageDets',
    'code_str, line_no, advisor_name, warning, message')

PYTHON_CODE_START = '__python_code_start__'
PYTHON_CODE_END = '__python_code_end__'

MD_PYTHON_CODE_START = '::python'

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MESSAGE_TYPES = [BRIEF, MAIN, EXTRA]

ANON_NAME = 'Anonymous'

AST_OUTPUT_XML = 'ast_output.xml'

XML_ROOT_BODY_ASSIGN_VALUE = 'body/Assign/value'
XML_ROOT_BODY = 'body'

## To see what elements are named look in AST_OUTPUT_XML
## e.g. <For lineno="3" col_offset="0"> is "For"
LIST_ELEMENT_TYPE = 'List'
LISTCOMP_ELEMENT_TYPE = 'ListComp'
DICT_ELEMENT_TYPE = 'Dict'
NUM_ELEMENT_TYPE = 'Num'
STR_ELEMENT_TYPE = 'Str'
FOR_ELEMENT_TYPE = 'For'

INT_TYPE = 'int'
FLOAT_TYPE = 'float'
STR_TYPE = 'str'
DATETIME_TYPE = 'datetime'
BOOLEAN_TYPE = 'bool'

TYPE2NAME = {
    INT_TYPE: 'integer',
    FLOAT_TYPE: 'float',
    STR_TYPE: 'string',
    DATETIME_TYPE: 'datetime object',
    BOOLEAN_TYPE: 'boolean',
}

EXAMPLES_OF_TYPES = {
    INT_TYPE: [123, 9, 17, 20, 100, 2020, 16],
    FLOAT_TYPE: [1.2345, 0.667, 0.1, 0.001, 10.0],
    STR_TYPE: ['apple', 'banana', 'kiwifruit', 'Auckland, New Zealand'],
    DATETIME_TYPE: [
        datetime.date(2020, 4, 4),
        datetime.date(1066, 10, 14),
        datetime.datetime.today(), ],
    BOOLEAN_TYPE: [True, False],
}

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

DEMO_SNIPPET = """\
import datetime
from math import pi as π
mixed_keys = {1: 'cat', '1': 'dog'}
mixedTypes = [
    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
    π, 5, 1.234, 'Noor', False,
]
names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
names_lower = [name.lower() for name in names]
name_lengths = []
for name in names:
    name_lengths.append(len(name))
fullName = 'Guido van Rossum'
evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
empty = []
myint = 666
myfloat = 6.667
myscinot = 1.23E-7
"""
TEST_SNIPPET = """\
capitals = {'NZ': 'Auckland', 'France': 'Paris'}
"""
BROKEN_TEST_SNIPPET = """\
meals = [['weetbix', 'toast'], ]
meals[0] = ['muesli', ]
"""
