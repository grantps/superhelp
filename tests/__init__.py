## cd ~/projects/superhelp && superhelp/env/bin/python3 -m nose
import astpath
from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false  # @UnusedImport @UnresolvedImport
try:
    from ..superhelp import conf  # @UnresolvedImport
    from ..superhelp import ast_funcs  # @UnresolvedImport
    from ..superhelp.messages import get_separated_messages_dets  # @UnresolvedImport
    from ..superhelp.utils import get_tree, xml_from_tree  # @UnresolvedImport
except (ImportError, ValueError):
    from pathlib import Path
    import sys
    parent = str(Path.cwd().parent)
    sys.path.insert(0, parent)
    from superhelp import conf  # @Reimport
    from superhelp import ast_funcs  # @Reimport
    from superhelp.messages import get_separated_messages_dets  # @Reimport
    from superhelp.utils import get_tree, xml_from_tree  # @Reimport

conf.INCLUDE_LINTING = False
conf.RECORD_AST = True

def get_actual_source_freqs(messages_dets, expected_source_freqs):
    """
    Check the message sources are as expected. Note - we don't have to know what
    messages generated from advisors in other modules will do - just what we
    expect from this module. So we don't specify what sources we expect - just
    those that we require (and how often) and those we ban (we expect those 0
    times).

    Note - exclude system-generated messages e.g. a message fails to run so we
    get a message all right but it is a message reporting the problem. Don't
    count those ;-).

    :param list messages_dets: list of MessageDets named tuples
    :param dict expected_source_freqs: keys are sources (strings) and values are
     integers. The integer should be set to 0 if we want to explicitly ban a
     source i.e. we do not expect it provide a message. E.g. if our list does
     not have mixed data types we do not expect a message saying there are.
    :return: whether it is as expected or not
    :rtype: bool
    """
    overall_snippet_messages_dets, block_level_messages_dets = messages_dets
    all_messages_dets = (
        overall_snippet_messages_dets + block_level_messages_dets)
    actual_source_freqs = {source: 0 for source in expected_source_freqs}
    for message_dets in all_messages_dets:
        if message_dets.source in expected_source_freqs:
            actual_source_freqs[message_dets.source] += 1  ## if we track any sources not in the expected list the dicts will vary even if the results for the tracked sources are exactly as expected and we'll fail the test when we shouldn't)
    return actual_source_freqs

def check_as_expected(test_conf):
    """
    :param list test_conf: list of tuples: snippet, dict of expected message
     sources and their expected frequencies
    """
    for snippet, expected_source_freqs in test_conf:
        tree = get_tree(snippet)
        xml = astpath.asts.convert_to_xml(tree)
        ast_funcs.store_ast_output(xml)
        snippet_block_els = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
        messages_dets = get_separated_messages_dets(
            snippet, snippet_block_els, xml)
        actual_source_freqs = get_actual_source_freqs(
            messages_dets, expected_source_freqs)
        assert_equal(actual_source_freqs, expected_source_freqs,
            (f"\n\nSnippet\n\n{snippet}\n\n"
             "didn't get messages as expected from the sources:"
             f"\n\nExpected:\n{expected_source_freqs}"
             f"\n\nActual:\n{actual_source_freqs}"
            )
        )

def get_actual_result(snippet, xpath, func):
    """
    Return actual result from running supplied function on first element
    matching xpath criteria.

    :param str snippet: valid snippet of Python code
    :param str xpath: valid xpath
    :param function func: function expecting first matching element as input
    """
    tree = get_tree(snippet)
    xml = xml_from_tree(tree)
    if conf.RECORD_AST:
        ast_funcs.store_ast_output(xml)
    el = xml.xpath(xpath)[0]
    actual_result = func(el)
    return actual_result

def get_repeated_lines(*, item='pass', lpad=16, n_lines=100):
    """
    :return: E.g.
     '''pass
     pass
     pass
     pass
     pass
     pass'''
    :rtype: str
    """
    repeated_lines = ('\n' + (lpad * ' ')).join([item]*n_lines)
    return repeated_lines
