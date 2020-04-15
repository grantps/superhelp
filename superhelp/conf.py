import datetime
import logging

LOG_LEVEL = logging.INFO

## When testing user-supplied snippets watch out for the BOM MS inserts via Notepad. AST chokes on it.

EXAMPLE_SNIPPET = """\
def sorted(my_list):
    sorted_list = my_list.sort()
    return sorted_list
"""

TEST_SNIPPET = """\
def sorted(my_list):
    sorted_list = my_list.sort()
    return sorted_list
"""

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
for name in ['Noor', 'Grant', ]:
    name_lengths.append(len(name))
fullName = 'Guido van Rossum'
evens_squared = [x**2 for x in range(1, 6) if x % 2 == 0]
empty = []
myint = 666
myfloat = 6.667
myscinot = 1.23E-7
my_tup = ('alpha', 'beta')
greeting = f"Hi {names[0]}!"
greeting = "Hi " + names[0] + "!"
def powerMe(num, *, power=2):
    poweredVal = num ** power
    return poweredVal
coord = ('lat', 'lon')
latitude = coord[0]
longitude = coord[1]
x, y = coord
people = set(['Sam', 'Avi', 'Terri', 'Noor'])
no_email = set(['Sam', 'Terri'])
people2email = people - no_email
empty_set = set()
len_word = len(fullName)
if len_word == 1:
    status = 'single-letter'
elif len_word < 4:
    status = 'short'
elif len_word > 12:
    status = 'long'
elif len_word > 20:
    status = 'very_long'
# else:
#     status = 'typical'
if len('chicken') > 2:
    print('cluck!')
phrase = "His age is %i" % 21

fruit = ['banana']
try:
    lunch = fruit[100]
except (IndexError, TypeError):
    print("No lunch for you!")
except Exception as e:
    print(f"Unknown error - details: {e}")

try:
    float('boat')
except ValueError:
    print("You can't float a boat! Only a number of some sort!")

try:
    names[100]
except Exception:
    print(names)

sorted_names = sorted(names)
faulty_val = names.sort()

## modified and given more problems and features, from https://stackoverflow.com/questions/61154079/sorting-using-list-built-in-method-and-user-defined-function-sorts-the-list-with
def sorted(*G, **kwargs):
    for i in range(len(G)):
        for j in range(1,len(G)):
            if G[j-1]<G[j]:
                G[j-1],G[j]=G[j],G[j-1]
G = [['Ahmad', 3.8], ['Rizwan', 3.68], ['Bilal', 3.9]]
sorted(G)
print(G)

from functools import wraps
def tweet(func):
    @wraps(func)
    def wrapper(message):
        func(message)
        print(f"I'm tweeting the message {message}")
    return wrapper

@tweet
def say(message):
    print(message)

say("sausage!")

def has_docstring():
    '''
    Hi
    '''
    pass
def lacks_proper_docstring():
    # Not a doc string
    pass
def lacks_any_docstring():
    666
    name = 'Grant'
    '''
    Ho
    '''
def random():
    '''
    This is line 1
    Line 2
    Line 3
    '''
    pass
def camelCase(a, b, c, d, f, *, g):
    '''
    This is line 1
    Line 2
    Line 3
    '''
    pass
"""

DEV_MODE = (LOG_LEVEL == logging.DEBUG)  ## updates AST output each run
AST_OUTPUT_XML = 'ast_output.xml'

PYTHON_CODE_START = '__python_code_start__'
PYTHON_CODE_END = '__python_code_end__'

MD_PYTHON_CODE_START = '::python'

BRIEF = 'Brief'  ## no spaces; used as labels and as parts of class names in CSS
MAIN = 'Main'
EXTRA = 'Extra'
MESSAGE_LEVELS = [BRIEF, MAIN, EXTRA]

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

MAX_BRIEF_FUNC_LOC = 35
MAX_BRIEF_FUNC_ARGS = 6
MIN_BRIEF_DOCSTRING = 3

NO_ADVICE_MESSAGE = ("No advice to give - looks fine :-). But if you think "
    "there should have been some advice given, contact grant@p-s.co.nz with "
    "the subject line 'Advice' and explain. Include a snippet to test as well.")
SYSTEM_MESSAGE = 'System message'

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
