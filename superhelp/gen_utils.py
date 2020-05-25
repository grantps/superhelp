from contextlib import contextmanager
from functools import partial
import inspect
import logging
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
from textwrap import dedent, wrap
import webbrowser

import ast

from . import code_execution, conf, name_utils
from lxml import etree
import astpath  # @UnresolvedImport

from astpath.asts import _set_encoded_literal, _strip_docstring

## Monkey-patch as at astpath Python 3.8 as at 2020-04-26
## Need to be able to tell val = 1 from val = '1' (that little detail ;-))
## Pull request fixing this was accepted and merged May 2020
def convert_to_xml(node, omit_docstrings=False, node_mappings=None):
    """Convert supplied AST node to XML."""
    possible_docstring = isinstance(
        node, (ast.FunctionDef, ast.ClassDef, ast.Module))

    xml_node = etree.Element(node.__class__.__name__)
    for attr in ('lineno', 'col_offset'):
        value = getattr(node, attr, None)
        if value is not None:
            _set_encoded_literal(
                partial(xml_node.set, attr),
                value
            )
    if node_mappings is not None:
        node_mappings[xml_node] = node

    node_fields = zip(
        node._fields,
        (getattr(node, attr) for attr in node._fields)
    )

    for field_name, field_value in node_fields:
        if isinstance(field_value, ast.AST):
            field = etree.SubElement(xml_node, field_name)
            field.append(
                convert_to_xml(
                    field_value,
                    omit_docstrings,
                    node_mappings,
                )
            )

        elif isinstance(field_value, list):
            field = etree.SubElement(xml_node, field_name)
            if possible_docstring and omit_docstrings and field_name == 'body':
                field_value = _strip_docstring(field_value)

            for item in field_value:
                if isinstance(item, ast.AST):
                    field.append(
                        convert_to_xml(
                            item,
                            omit_docstrings,
                            node_mappings,
                        )
                    )
                else:
                    subfield = etree.SubElement(field, 'item')
                    _set_encoded_literal(
                        partial(setattr, subfield, 'text'),
                        item
                    )

        elif field_value is not None:

            ## The only change is this immediate function call below
            ## add type attribute e.g. so we can distinguish strings from numbers etc
            ## <Constant lineno="1" col_offset="6" type="int" value="1"/>
            _set_encoded_literal(
                partial(xml_node.set, 'type'),
                type(field_value).__name__
            )

            _set_encoded_literal(
                partial(xml_node.set, field_name),
                field_value
            )

    return xml_node

astpath.asts.convert_to_xml = convert_to_xml


starting_num_space_pattern = r"""(?x)
    ^      ## start
    \d{1}  ## one digit
    \s{1}  ## one whitespace
    \S+    ## at least one non-whitespace
    """
starting_num_space_prog = re.compile(starting_num_space_pattern)

def get_items(raw_item_els):
    """
    Handles strings and numbers only. Everything else becomes conf.UNKNOWN_ITEM.

    :rtype: list
    """
    from . import ast_funcs  ## avoid circular import
    items = []
    for raw_el in raw_item_els:
        res = ast_funcs.val_dets(raw_el)
        if res is None:
            items.append(conf.UNKNOWN_ITEM)
        else:
            val, _needs_quoting = res
            items.append(val)
    return items

def ast_collection_items(named_el):
    """
    Get items in collection using AST only. Cope with unknowns using
    conf.UNKNOWN_ITEM and conf.UNKNOWN_ITEMS as appropriate.

    Warning - dicts may result in lists of key:value pairs with repeated keys if
    they are mapped to conf.UNKNOWN_ITEM. So always count items first before
    creating a dict from them at any stage otherwise the number of items will be
    understated.

    For List Comprehension, always return conf.UNKNOWN_ITEMS
    because it is not practical to evaluate values using AST.

    Throw exception if named_el not as expected.

    :return: list of items. These may include some conf.UNKNOWN_ITEMs if we
     can't resolve individual items e.g. results of functions like
     datetime.date(). If unable to get any results, e.g. ListComp, return
     conf.UNKNOWN_ITEMS
    :rtype: list or conf.UNKNOWN_ITEMS str
    """
    items = []
    tag = named_el.tag
    if tag == 'Dict':
        raw_key_els = named_el.xpath('keys')[0].getchildren()
        raw_val_els = named_el.xpath('values')[0].getchildren()
        keys = get_items(raw_key_els)
        vals = get_items(raw_val_els)
        items = list(zip(keys, vals))
    elif tag == 'Set':
        raw_val_els = named_el.xpath('elts')[0].getchildren()
        items = list(set(get_items(raw_val_els)))  ## inner set casting needed in case multiple Nones - just because they must be different to be in a set doesn't mean this code can tell the difference ;-)
    elif tag in ('List', 'Tuple'):
        raw_val_els = named_el.xpath('elts')[0].getchildren()
        items = get_items(raw_val_els)
    elif tag == 'ListComp':
        items = conf.UNKNOWN_ITEMS  ## impractical to evaluate using AST
    elif tag == 'Name':
        name_id = named_el.get('id')
        call_el = named_el.xpath('ancestor::Call')[-1]
        elts_els = call_el.xpath('args/List/elts | args/Tuple/elts')
        if len(elts_els) == 1:
            if name_id == 'dict':
                ## args/List/elts/Tuple should have one or more two-tuples
                ## convert to list of two-tuples
                tuple_elts_els = call_el.xpath('args/List/elts/Tuple/elts')
                tups_list = []
                for tuple_elts_el in tuple_elts_els:
                    raw_val_els = tuple_elts_el.getchildren()
                    tup_items = get_items(raw_val_els)
                    if len(tup_items) != 2:
                        raise Exception("All tuples in a dict definition should"
                            " be two-tuples (key, value)")
                    tups_list.append(tup_items)
                items = tups_list
            else:
                raw_val_els = elts_els[0].getchildren()
                items = get_items(raw_val_els)
        elif len(elts_els) == 0 and name_id in ('list', 'set', 'tuple'):
            items = []  ## empty collection that's why no elts_els
        else:
            items = conf.UNKNOWN_ITEMS
    else:
        raise Exception(f"Unexpected named_el: '{tag}'")
    return items

def get_collections_dets(named_els, block_dets, *,
        collection_plural, truncated_items_func, execute_code=True):
    """
    Get information on collections - names with associated items, plus a string
    message (empty str if no oversized items) which can be assembled as part of
    a full helper message.

    :param list named_els: list of Assign elements which have collections as the
     value e.g. Assign/value/List (Dict, Set, Tuple, List, ListComp etc)
    :return: names_items: list of (name, items) tuples, and oversized_msg (str).
     items is either a list (in the case of a dict, a list of (k, v) tuples) or
     conf.UNKNOWN_ITEMS.
    :rtype: list
    """
    names_items = []
    oversized_names = []
    for named_el in named_els:
        names_dets = name_utils.get_assigned_names(named_el)
        for name_dets in names_dets:
            if execute_code:
                items = code_execution.execute_collection_dets(
                    block_dets, name_dets)
                if items == conf.UNKNOWN_ITEMS:
                    items = ast_collection_items(named_el)
            else:
                items = ast_collection_items(named_el)
            if items != conf.UNKNOWN_ITEMS:
                if len(items) > conf.MAX_ITEMS_EVALUATED:
                    items = truncated_items_func(items)
                    oversized_names.append(name_dets.name_str)
                names_items.append((name_dets.name_str, items))
    if oversized_names:
        multi_oversized = len(oversized_names) > 1
        if multi_oversized:
            nice_names = get_nice_str_list(oversized_names, quoter='`')
            oversized_msg = layout_comment(f"""\

            Because the following {collection_plural} were large SuperHELP has
            only examined the first {conf.MAX_ITEMS_EVALUATED} items:
            {nice_names}
            """)
        else:
            oversized_msg = layout_comment(f"""\

            Because `{name_dets.name_str}` is large SuperHELP has only examined
            the first {conf.MAX_ITEMS_EVALUATED} items.
            """)
    else:
        oversized_msg = ''
    return names_items, oversized_msg

def open_output_folder():
    """
    On Linux, webbrowser delegates to xdg-open which checks mime type to decide
    what gets to open something. Directories get delegated by xdg-open to
    nautilus, for example, and html to the webbrowser usually.

    So even though web browsers display the contents of folders very easily we
    can't get xdg-open to delegate a directory to a browser. So I'm cheating - I
    make a wrapper page which has a link to the desired folder uri. Where
    there's a will there's a way.
    """
    project_output_tmpdir = get_superhelp_tmpdir(
        folder=conf.SUPERHELP_PROJECT_OUTPUT)
    project_output_url = project_output_tmpdir.as_uri()
    gen_tmpdir = get_superhelp_tmpdir(folder=conf.SUPERHELP_GEN_OUTPUT)
    with make_open_tmp_file('project_help.html',
            superhelp_tmpdir=gen_tmpdir, mode='w') as tmp_dets:
        _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
        internal_css = dedent("""\
        body {
          background-color: white;
          margin: 40px 70px 20px 70px;
          max-width: 700px;
        }
        h1, h2 {
          font-weight: bold;
        }
        h1 {
          color: #0072aa;
          font-size: 24px;
        }
        h2 {
          color: black;
          font-size: 18px;
          margin-top: 24px;
        }
        p {
          color: black;
          font-size: 14px;
        }
        svg {
          height: 100px;
          width: 100px;
        }
        a:link, a:visited, a:hover, a:active {
          color: #0072aa;
          border-bottom: 1px solid #0072aa;
          text-decoration: none;
        }
        """)
        head = conf.HTML_HEAD % {'internal_css': internal_css}
        body_inner = f"""\
        <a href='{project_output_url}'>Individual help files for your
        project</a>
        """
        html = f"""\
        <!DOCTYPE html>
        <html lang="en">
        {head}
        <body>
        {conf.LOGO_SVG}
        <h1>SuperHELP for your project</h1>
        <h2>Warning</h2>
        <p>The output for this project is stored in a temporary folder - if you
        want to keep the results you will need to shift
        '{project_output_tmpdir}' somewhere else</p>
        {body_inner}
        </body>
        </html>"""
        tmp_fh.write(html)
    webbrowser.open(fpath.as_uri())

def get_tree(snippet):
    try:
        tree = ast.parse(snippet)
    except SyntaxError as e:
        raise SyntaxError(
            f"Oops - something seems broken in the snippet - details: {e}")
    return tree

def xml_from_tree(tree):
    xml = astpath.asts.convert_to_xml(tree)
    return xml

def get_intro(file_path, *, multi_block=False):
    if not file_path:
        if multi_block:
            intro = (f"Help is provided for the supplied code as a whole and "
                "for each block of code as appropriate. If there is nothing to "
                "say about a block it is skipped.")
        else:
            intro = ''
    else:
        intro = (f"Help is provided for '{file_path}' as a whole and for each "
            "block of code as appropriate. If there is nothing to say about a "
            "block it is skipped.")
    return intro

def get_code_desc(file_path):
    if file_path:
        code_desc = file_path
    else:
        code_desc = 'Overall Snippet'
    return code_desc

def get_line_numbered_snippet(snippet):
    snippet_lines = snippet.strip('\n').split('\n')
    n_lines = len(snippet_lines)
    width = len(str(n_lines))
    new_snippet_lines = []
    for n, line in enumerate(snippet_lines, 1):
        new_snippet_lines.append(f"{n:>{width}}   {line}".rstrip())
    lined_snippet = '\n'.join(new_snippet_lines)
    return lined_snippet

def get_introspected_file_path():
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

def get_os_platform():
    platforms = {
        'Linux': conf.LINUX, 'Windows': conf.WINDOWS, 'Darwin': conf.MAC}
    os_platform = platforms.get(platform.system())
    return os_platform

def clean_path_name(raw_path):
    """
    Get a path we can use in a url or file path.
    """
    clean_path = (raw_path
        .replace('...', '_')
        .replace('/', '_')
        .replace('\\', '_'))
    return clean_path

def get_superhelp_tmpdir(folder='superhelp'):
    tmpdir = tempfile.gettempdir()
    superhelp_tmpdir = os.path.join(tmpdir, folder)
    return Path(superhelp_tmpdir)

@contextmanager
def make_open_tmp_file(fname, *, superhelp_tmpdir=None, mode='w'):
    """
    Note - file needs to be closed for changes to be saved to the file -
    otherwise it will be 0 bytes. Up to client code to ensure it is closed and
    properly available for subsequent steps.
    """
    try:
        if not superhelp_tmpdir:
            superhelp_tmpdir = get_superhelp_tmpdir()
        superhelp_tmpdir.mkdir(exist_ok=True)
        tmp_fh = tempfile.NamedTemporaryFile(
            mode=mode, delete=False, dir=superhelp_tmpdir)
        randomly_named_fpath = Path(tmp_fh.name)
        fpath = Path(randomly_named_fpath.parent) / fname
        os.rename(randomly_named_fpath, fpath)
        yield superhelp_tmpdir, tmp_fh, fpath
    finally:
        tmp_fh.close()

def get_python_version():
    major, minor = sys.version_info[:2]
    return f"{major}.{minor}"

def get_nice_str_list(items, *, item_glue=', ', quoter='`'):
    """
    Get a nice English phrase listing the items.

    :param sequence items: individual items to put into a phrase.
    :param str quoter: default is backtick because it is expected that the most
     common items will be names (variables).
    :return: nice phrase
    :rtype: str
    """
    nice_str_list = item_glue.join(
        [f"{quoter}{item}{quoter}" for item in items[:-1]])
    if nice_str_list:
        nice_str_list += f"{item_glue}and "
    nice_str_list += f"{quoter}{items[-1]}{quoter}"
    return nice_str_list

def _get_quoted_pair(left, right, pair_glue, left_quoter, right_quoter):
    return (
        f"{left_quoter}{left}{left_quoter}"
        f"{pair_glue}"
        f"{right_quoter}{right}{right_quoter}"
    )

def get_nice_pairs(pairs, *, pair_glue=': ', left_quoter='`', right_quoter='`'):
    """
    Get a nice English phrase listing paired items.

    :param sequence pairs: a sequence of two-tuples
    :param str pair_glue: how to join items in pair
     e.g. ': ' --> a: b
     e.g. ' is assigned to ' --> a is assigned to b
    :param str quoter: default is backtick because it is expected that the most
     common items will be names (variables).
    :return: nice phrase
    :rtype: str
    """
    nice_pairs_list = ', '.join(
        _get_quoted_pair(left, right, pair_glue, left_quoter, right_quoter)
        for left, right in pairs[:-1])
    if nice_pairs_list:
        nice_pairs_list += ', and '
    final_left, final_right = pairs[-1]
    nice_pairs_list += _get_quoted_pair(
        final_left, final_right, pair_glue, left_quoter, right_quoter)
    return nice_pairs_list

def int2nice(num):
    """
    :return: nicer version of number ready for use in sentences
    :rtype: str
    """
    nice = {
        0: 'no',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
        6: 'six',
        7: 'seven',
        8: 'eight',
        9: 'nine',
        10: 'ten',
        11: 'eleven',
        12: 'twelve',
    }
    return nice.get(num, num)

def int2first_etc(num):
    """
    :return: first for 1, second for 2 etc
    :rtype: str
    """
    nice = {
        1: 'first',
        2: 'second',
        3: 'third',
        4: 'fourth',
        5: 'fifth',
        6: 'sixth',
        7: 'seventh',
        8: 'eighth',
        9: 'nineth',
        10: 'tenth',
        11: 'eleventh',
        12: 'twelfth',
    }
    return nice.get(num, num)

def layout_comment(raw_comment, *, is_code=False):
    """
    Layout comment ready for MD. Handles dedenting and code.

    Doesn't break up long lines which are titles otherwise the subsequent parts
    won't carry appropriate heading-level formatting.

    :param str raw_comment: Comment ready to be dedented, consolidated, split
     etc. Usually will have new line characters at start and end to ensure MD
     doesn't lump paragraphs together. Extra new lines have no effect in the
     output but might be useful in the source e.g. to allow automatic line
     breaking after editing content.
    :param bool is_code: if True then special code markers are inserted. These
     are replaced by the appropriate code markers in the displayer.
    :rtype: str
    """
    if '`' in raw_comment and is_code:
        logging.debug("Backtick detected in code which is probably a mistake")
    if is_code:
        lines = (
            [conf.PYTHON_CODE_START]
            + dedent(raw_comment).split('\n')
            + [conf.PYTHON_CODE_END]
        )
        indented_lines = [f"{' ' * 4}{line}" for line in lines]
        comment = f'\n'.join(indented_lines) + '\n'  ## new line at end needed otherwise content of next str (if any) becomes part of code highlighting
    else:
        raw_paragraphs = dedent(raw_comment).split('\n\n')  ## we only split paragraphs if two new lines
        new_paragraphs = []
        for raw_paragraph in raw_paragraphs:
            ## replace internal new lines only - we need to preserve the outer ones
            n_start_new_lines = (
                len(raw_paragraph) - len(raw_paragraph.lstrip('\n')))
            n_end_new_lines = (
                len(raw_paragraph) - len(raw_paragraph.rstrip('\n')))
            paragraph = raw_paragraph.strip()
            one_line_paragraph = paragraph.replace('\n', ' ')  ## actually continuations of same line so no need to put on separate lines
            special_line = False
            res = starting_num_space_prog.match(one_line_paragraph)
            if res is not None:
                special_line = True
            if one_line_paragraph.startswith((
                    '#',  ## could be one hash or multiple depending on heading level
                    '* '  ## trying to detect bulleted (unordered) lists
                )):
                special_line = True
            if special_line:
                wrapped_paragraph_lines = [one_line_paragraph, ]
            else:
                wrapped_paragraph_lines = wrap(one_line_paragraph)
            new_paragraph = (
                (n_start_new_lines * '\n\n')
                + '\n'.join(wrapped_paragraph_lines)
                + (n_end_new_lines * '\n\n')
            )
            new_paragraphs.append(new_paragraph)
        comment = '\n' + '\n\n'.join(new_paragraphs)
    return comment

def get_docstring_start(docstring):
    docstring_start = (
        docstring.lstrip('\n').split('\n\n')[0].strip().replace('\n    ', ' '))
    return docstring_start
