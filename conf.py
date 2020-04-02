from collections import namedtuple

MessageDets = namedtuple('MessageDets',
    'code_str, line_no, advisor_name, warning, element_type, message')

MD_PYTHON_CODE_START = '::python'

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MESSAGE_TYPES = [BRIEF, MAIN, EXTRA]

ANON_NAME = 'Anonymous'

## Only include elements which are safe to exec
## To see what 
LIST_ELEMENT_TYPE = 'List'
LISTCOMP_ELEMENT_TYPE = 'ListComp'
NUM_ELEMENT_TYPE = 'Num'
STR_ELEMENT_TYPE = 'Str'

INT_CLASS = 'int'
FLOAT_CLASS = 'float'
STR_CLASS = 'str'
DATETIME_CLASS = 'datetime'

CLASS2NAME = {
    INT_CLASS: 'integer',
    FLOAT_CLASS: 'float',
    STR_CLASS: 'string',
    DATETIME_CLASS: 'datetime object'
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

ADVANCED_DEMO_SNIPPET = """\
import datetime
import math
mixed = [
    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
    math.pi, 5, 1.234, 'Noor',
]
names = ['Noor', 'Grant', 'Hyeji', 'Vicky', 'Olek', 'Marzena', 'Jess', 'Nicole']
names_lower = [name.lower() for name in names]
empty = []
myint = 666
"""
DEMO_SNIPPET = """\
import datetime
from math import pi
mixed = [
    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
    pi, 5, 1.234, 'Noor',
]
person = 'Guido van Rossum'
evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
empty = []
myint = 666
myfloat = 6.667
myscinot = 1.23E-7
"""
TEST_SNIPPET = """\
import datetime
import math
from math import pi as pie
mixed = [
    datetime.datetime.strptime('2020-02-10', '%Y-%m-%d'),
    math.pi, 5, 1.234, 'Noor',
]
"""
