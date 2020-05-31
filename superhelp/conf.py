import datetime
import logging

t = True
f = False

## =============================================================================

## Release settings in (). Enforced by Makefile using good old sed :-)

CLI = 'cli'
HTML = 'html'
MD = 'md'

c = CLI
h = HTML
m = MD

RECORD_AST = f  ## (f)
OUTPUT = h  ## set html as default output (h)
SHOW_OUTPUT = t  ## f is only ever used when testing pre-display (t)
INCLUDE_LINTING = t  ## f when running unit tests to massively speed them up (otherwise every snippet in tests is linted each time) (t)
LOG_LEVEL = logging.INFO  ## (logging.INFO)
## =============================================================================

## When testing user-supplied snippets watch out for the BOM MS inserts via Notepad. AST chokes on it.
## All snippets here should be raw strings (see https://stackoverflow.com/questions/53636723/python-parsing-code-with-new-line-character-in-them-using-ast)
TEST_SNIPPET = r"""
import os, requests, conf
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
UNKNOWN_ITEM = '__unknown item__'
UNKNOWN_ITEMS = '__unknown items__'

INT_TYPE = 'int'
FLOAT_TYPE = 'float'
NUM_TYPE = 'number'
STR_TYPE = 'str'
DATETIME_TYPE = 'datetime'
DATE_TYPE = 'date'
BOOLEAN_TYPE = 'bool'
LIST_TYPE = 'list'
DICT_TYPE = 'dict'
TUPLE_TYPE = 'tuple'

TYPE2NAME = {
    INT_TYPE: 'integer',
    FLOAT_TYPE: 'float',
    NUM_TYPE: 'number (specific type unknown)',
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
    DATETIME_TYPE: [  ## use strings so it is already quoted ready for use as an example
        datetime.datetime(2020, 4, 4),
        datetime.datetime(1066, 10, 14),
        datetime.datetime(1995, 9, 14),
    ],
    DATE_TYPE: [  ## use strings so it is already quoted ready for use as an example
        datetime.date(2020, 4, 4),
        datetime.date(1066, 10, 14),
        datetime.date(1995, 9, 14),
    ],
    BOOLEAN_TYPE: [True, False],
    LIST_TYPE: [[10, 2], [-3, 20], [44, -180]],
    DICT_TYPE: [{'x': 10, 'y': 2}, {'x': -3, 'y': 20}, {'x': 44, 'y': -180}],
    TUPLE_TYPE: [(10, 2), (-3, 20), (44, -180)],
}

STD_NAME = 'std_name'
DICT_KEY_NAME = 'dict_key_name'
OBJ_ATTR_NAME = 'obj_attr_name'

NON_STD_EL_KEYS = ('lineno', 'col_offset')

MAX_BRIEF_FUNC_LOC = 35
MAX_BRIEF_FUNC_ARGS = 6
MIN_BRIEF_DOCSTRING = 3
MIN_BRIEF_NAME = 3
MAX_BRIEF_NESTED_BLOCK = 20
MIN4ANY_OR_ALL = 3
MAX_ITEMS_EVALUATED = 25
MAX_PROJECT_MODULES = 50
MAX_FILE_PATH_IN_HEADING = 75

FUNCTION_LBL = 'function'
METHOD_LBL = 'method'

EMAIL2USE = 'superhelp@p-s.co.nz'
TWITTER_HANDLE = 'PythonSuperHELP'

WARNINGS_ONLY_MSG = ("Only displaying warnings. "
    "To see all help, set warnings only option to False")
ALL_HELP_SHOWING_MSG = ("Displaying all help. "
    "To only see warnings, set warnings only option to True")

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

FORCE_SPLIT = '__force_split__'

DARK = 'dark'
LIGHT = 'light'

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
POPULAR_LIBS = ['requests', 'flask', 'django', ]

SUPERHELP_PROJECT_OUTPUT = 'superhelp_project_output'
SUPERHELP_GEN_OUTPUT = 'superhelp_output'

HTML_HEAD = f"""\
<head>
<meta charset="utf-8">
<meta content="IE=edge" http-equiv="X-UA-Compatible">
<title>SuperHELP - Help for Humans!</title>
<style type="text/css">
%(internal_css)s
</style>
</head>"""

INTERNAL_CSS = """\
body {
  background-color: white;
  %(margin_css)s
  %(max_width_css)s
}
h1, h2 {
  color: #0072aa;
  font-weight: bold;
}
h1 {
  font-size: 16px;
}
h2 {
  font-size: 14px;
  margin-top: 24px;
}
h3 {
  font-size: 12px;
}
h4 {
  font-size: 11px;
}
h5 {
  font-size: 9px;
  font-style: italic;
}
p {
  font-size: 10px;
}
li {
  font-size: 10px;
}
label {
  font-size: 12px;
}
blockquote {
  font-style: italic;
  color: #666666;
}
blockquote p {
  font-size: 13px;
}
svg {
  height: 50px;
  width: 60px;
}
.warning {
  border-radius: 2px;
  padding: 12px 6px 6px 12px;
  margin: 10px 0 0 0;
  border: 2px solid #0072aa;
}

#star {
  padding: 9px 10px 10px 10px;
  background-color: #0072aa;
  color: white;
  font-size: 15px;
  font-weight: bold;
  border-radius: 8px;
  text-align: center;
}
#star a:link, #star a:visited, #star a:hover, #star a:active {
  color: white;
  border-bottom: 1px solid white;
  text-decoration: none;
}
#star #grow {
  font-size: 20px;
}

.help {
  display: none;
}
.help.help-visible {
  display: inherit;
}
%(code_css)s
"""

LOGO_SVG = """\
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="100.11089mm"
   height="79.607109mm"
   viewBox="0 0 100.11089 79.607109"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.4 (5da689c313, 2019-01-14)"
   sodipodi:docname="superhelp_logo.svg"
   inkscape:export-filename="/home/g/projects/superhelp/superhelp/store/superhelp_logo.png"
   inkscape:export-xdpi="96"
   inkscape:export-ydpi="96">
  <defs
     id="defs2">
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4972"
       is_visible="true"
       pattern="m 60.80692,207.585 -0.62276,-0.0405 -0.15389,-0.6048 0.527651,-0.33326 0.479996,0.39885 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4944"
       is_visible="true"
       pattern="m 58.866112,205.1261 h 0.701582 v 0.66817 h -0.701582 z"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4907"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4889"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4861"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4820"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4721"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0.1"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4694"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect935"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
  </defs>
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="1"
     inkscape:pageshadow="2"
     inkscape:zoom="1.979899"
     inkscape:cx="76.737316"
     inkscape:cy="121.00951"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     inkscape:window-width="1869"
     inkscape:window-height="1056"
     inkscape:window-x="1971"
     inkscape:window-y="24"
     inkscape:window-maximized="1"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0"
     inkscape:pagecheckerboard="false" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-53.753912,-82.960833)">
    <g
       transform="translate(-57.326112,-175.59945)"
       id="g9171">
      <path
         inkscape:connector-curvature="0"
         id="path4991-3-6"
         transform="matrix(0.26458333,0,0,0.26458333,-8.3176424,-7.9183424)"
         d="m 591.57422,1011.6934 a 83.098512,82.305791 18.437406 0 0 -53.05664,20.1914 83.098512,82.305791 18.437406 0 0 -26.49805,78.3183 83.098512,82.305791 18.437406 0 0 54.18164,61.5059 l -0.0371,0.1113 123.08203,41.0332 -2.51171,7.6485 -123.47461,-41.1661 v 0 l -77.85938,-25.957 a 82.244946,81.781039 18.437412 0 0 -1.26562,38.1523 82.244946,81.781039 18.437412 0 0 54.88671,61.3047 l 0.004,-0.01 123.56055,41.1914 -0.008,0.021 a 82.216504,82.216504 0 0 0 0.46094,0.1309 l 0.33594,0.1113 0.006,-0.016 a 82.216504,82.216504 0 0 0 80.125,-16.7149 82.216504,82.216504 0 0 0 25.77344,-78.4648 82.216504,82.216504 0 0 0 -53.91602,-60.75 v 0 l -0.16992,-0.057 a 82.216504,82.216504 0 0 0 -1.30274,-0.4551 l -0.006,0.02 -121.01758,-40.3458 2.64843,-7.83 119.71485,39.9121 -0.002,0.01 78.07226,26.0293 c 3.44134,-12.4392 14.87561,-39.3166 12.27344,-51.9727 -5.95174,-28.611 -37.64693,-38.2382 -65.52734,-47.4199 -0.10692,-0.035 -0.21742,-0.072 -0.32422,-0.1074 l -121.63282,-40.5508 -0.0117,0.033 a 83.098512,82.305791 18.437406 0 0 -26.5039,-3.9062 z"
         style="fill:#0072aa;fill-opacity:1;stroke:none;stroke-width:32.70064163;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 273.07885,208.13282 a 3.2002347,3.2002347 0 0 1 3.20327,-3.19481 3.2002347,3.2002347 0 0 1 3.1972,3.20089 3.2002347,3.2002347 0 0 1 -3.1985,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="208.13824"
         sodipodi:cx="276.27908"
         sodipodi:type="arc"
         id="path5097-9-2"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 227.2124,219.8216 a 3.2002347,3.2002347 0 0 1 3.20327,-3.19481 3.2002347,3.2002347 0 0 1 3.19719,3.20089 3.2002347,3.2002347 0 0 1 -3.19849,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="219.82703"
         sodipodi:cx="230.41263"
         sodipodi:type="arc"
         id="path5097-0-7-8"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 258.29068,242.97 a 3.2002347,3.2002347 0 0 1 3.20327,-3.1948 3.2002347,3.2002347 0 0 1 3.19719,3.20089 3.2002347,3.2002347 0 0 1 -3.1985,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="242.97543"
         sodipodi:cx="261.49091"
         sodipodi:type="arc"
         id="path5097-0-9-7-8"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
    </g>
  </g>
</svg>
"""
