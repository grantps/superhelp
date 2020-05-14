from functools import partial
import logging
from os import rename
from pathlib import Path
import platform
import re
import sys
import tempfile
from textwrap import dedent, wrap

import ast

from . import conf
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

def get_line_numbered_snippet(snippet):
    snippet_lines = snippet.split('\n')
    n_lines = len(snippet_lines)
    width = len(str(n_lines))
    new_snippet_lines = []
    for n, line in enumerate(snippet_lines, 1):
        new_snippet_lines.append(f"{n:>{width}}   {line}".rstrip())
    lined_snippet = '\n'.join(new_snippet_lines)
    return lined_snippet

def get_os_platform():
    platforms = {
        'Linux': conf.LINUX, 'Windows': conf.WINDOWS, 'Darwin': conf.MAC}
    os_platform = platforms.get(platform.system())
    return os_platform

def make_open_tmp_file(fname, mode='w'):
    """
    Note - file needs to be closed for changes to be saved to the file -
    otherwise it will be 0 bytes. Up to client code to ensure it is closed and
    properly available for subsequent steps.
    """
    tmp_fh = tempfile.NamedTemporaryFile(mode=mode, delete=False)
    randomly_named_fpath = Path(tmp_fh.name)
    fpath = Path(randomly_named_fpath.parent) / fname
    rename(randomly_named_fpath, fpath)
    return tmp_fh, fpath

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
