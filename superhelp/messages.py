from dataclasses import dataclass
import logging

from lxml.etree import _Element

from superhelp.ast_funcs import general as ast_gen
from superhelp import conf, helpers
from superhelp.gen_utils import get_docstring_start, get_tree, layout_comment as layout, xml_from_tree
from superhelp.helpers import HelperSpec

@dataclass
class BlockSpec:
    """
    Top-level code block with details
    """
    element: _Element
    pre_block_code_str: str  ## The code up until the line we are interested in needs to be run - it may depend on names from earlier
    block_code_str: str
    first_line_no: int

@dataclass
class MessageLevelStrs:
    """
    The actual text per level (brief, main, extra)
    """
    brief: str
    main: str
    extra: str = ''

@dataclass
class MessageSpec:
    """
    All the bits and pieces that might be needed to craft a message
    """
    code_str: str  ## The block of code the message relates to
    message_level_strs: MessageLevelStrs
    first_line_no: int
    warning: bool
    source: str  ## A unique identifier of the source of message - useful for auditing / testing

def get_block_specs(snippet: str, snippet_block_els) -> list[BlockSpec]:
    """
    Returning a list of all the details needed to process a line
    (namely BlockSpec dataclasses)

    Note - lines in the XML sit immediately under body.
    """
    snippet_lines = snippet.split('\n')
    block_specs = []
    for snippet_block_el in snippet_block_els:
        first_line_no, last_line_no, _el_lines_n = ast_gen.get_el_lines_dets(snippet_block_el)
        block_code_str = '\n'.join(snippet_lines[first_line_no - 1: last_line_no]).strip()
        pre_block_code_str = '\n'.join(snippet_lines[0: first_line_no - 1]).strip() + '\n'
        block_specs.append(BlockSpec(snippet_block_el, pre_block_code_str, block_code_str, first_line_no))
    return block_specs

def get_message_spec_from_input(helper_spec: HelperSpec, *, helper_input, code_str: str, xml: str, first_line_no,
        execute_code=True, repeat=False) -> MessageSpec | None:  ## TODO:
    """
    :param helper_spec: details of the helper e.g. name, function,
     etc depending on type of HelperSpec (e.g. IndivBlockHelperSpec)
    :param helper_input: the main input to the helper function e.g. block_spec, block_specs, or snippet_str.
    """
    name = helper_spec.helper_name
    docstring = helper_spec.helper.__doc__
    if not docstring:
        raise Exception(f'Helper "{name}" lacks a docstring - add one!')
    try:
        message_level_strs = helper_spec.helper(helper_input, xml=xml, execute_code=execute_code, repeat=repeat)  ## some helpers respond to execute_code or xml and some don't so need to mop up **_kwargs
    except Exception as e:
        brief_name = '.'.join(name.split('.')[-2:])  ## last two parts only
        brief = (
            layout(f"""\
                ### Helper "`{brief_name}`" unable to run

                Helper {brief_name} unable to run. Helper description:
                """)
            +  ## show first line of docstring (subsequent lines might have more technical, internally-oriented comments)
            layout(get_docstring_start(docstring) + '\n')
            +
            layout(str(e))
        )
        message_level_strs = MessageLevelStrs(brief, brief)
        source = conf.SYSTEM_MESSAGE
        warning = True
    else:
        source = name
        warning = helper_spec.warning
        if message_level_strs is None:
            return None
    message_spec = MessageSpec(code_str, message_level_strs, first_line_no, warning, source=source)
    return message_spec

def _get_ancestor_block_element(element):
    """
    The item immediately under body that this element is under.
    """
    ancestor_elements = element.xpath('ancestor-or-self::*')
    ancestor_block_element = ancestor_elements[2]  ## [0] will be Module, 1 is body, and blocks are the children of body
    return ancestor_block_element

def _get_filtered_block_specs(helper_spec, xml, block_specs) -> list[BlockSpec]:
    """
    Identify source block elements according to xpath supplied. Then filter block_specs accordingly.
    """
    matching_elements = xml.xpath(helper_spec.xpath)
    if matching_elements:
        logging.debug(f"{helper_spec.helper_name} had at least one match")
    else:
        logging.debug(f"{helper_spec.helper_name} had no matches")
    filt_block_elements = set([_get_ancestor_block_element(element) for element in matching_elements])
    filtered_block_specs = [block_spec for block_spec in block_specs
        if block_spec.element in filt_block_elements]
    if filtered_block_specs:
        logging.debug(f"{helper_spec.helper_name} had at least one block")
    else:
        logging.debug(f"{helper_spec.helper_name} had no blocks")
    return filtered_block_specs

def get_block_level_message_specs(block_specs, xml: str, *,
        warnings_only=False, execute_code=True, repeat_set=None) -> list[MessageSpec]:
    """
    For each helper, get advice on every relevant block.
    Element type specific helpers process filtered block_specs;
    all block helpers process all blocks (as you'd expect ;-)).

    As we iterate through the blocks, only the first block under a helper should get the full message.
    """
    message_specs = []
    for helper_spec in helpers.INDIV_BLOCK_HELPERS:
        logging.debug(f"About to process '{helper_spec.helper_name}'")
        if warnings_only and not helper_spec.warning:
            continue
        element_filtering = helper_spec.xpath is not None
        if element_filtering:
            filtered_block_specs = _get_filtered_block_specs(helper_spec, xml, block_specs)
            block_specs2use = filtered_block_specs
            logging.debug(
                f"'{helper_spec.helper_name}' has element filtering for {len(block_specs2use)} matching blocks")
        else:  ## no filtering by element type so process all blocks
            block_specs2use = block_specs
        for block_spec in block_specs2use:
            repeat = (helper_spec.helper_name in repeat_set)
            message_spec = get_message_spec_from_input(helper_spec,
                helper_input=block_spec, code_str=block_spec.block_code_str, xml=xml,
                first_line_no=block_spec.first_line_no,
                execute_code=execute_code, repeat=repeat)
            if message_spec:
                repeat_set.add(helper_spec.helper_name)
                message_specs.append(message_spec)
    return message_specs

def get_overall_snippet_message_specs(snippet, block_specs, *,
        warnings_only=False, execute_code=True, repeat_set=None) -> list[MessageSpec]:
    """
    Returns messages which apply to snippet as a whole, not just specific blocks.
    E.g. looking at every block to look for opportunities to unpack. Or reporting on linting results.
    """
    tree = get_tree(snippet)
    xml = xml_from_tree(tree)
    message_specs = []
    all_helpers_dets = helpers.MULTI_BLOCK_HELPERS + helpers.SNIPPET_STR_HELPERS
    for helper_spec in all_helpers_dets:
        logging.debug(f"About to process '{helper_spec.helper_name}'")
        if warnings_only and not helper_spec.warning:
            continue
        if helper_spec.input_type == conf.InputType.BLOCKS_SPECS:
            helper_input = block_specs
        elif helper_spec.input_type == conf.InputType.SNIPPET_STR:
            helper_input = snippet
        else:
            raise Exception(f"Unexpected input_type: '{helper_spec.input_type}'")
        repeat = (helper_spec.helper_name in repeat_set)
        message_spec = get_message_spec_from_input(helper_spec,
            helper_input=helper_input, code_str=snippet, xml=xml, first_line_no=None,
            execute_code=execute_code, repeat=repeat)
        if message_spec:
            repeat_set.add(helper_spec.helper_name)
            message_specs.append(message_spec)
    return message_specs

def get_separated_message_specs(snippet: str, snippet_block_els, xml, *,
        warnings_only=False, execute_code=True, repeat_set=None) -> tuple[list[MessageSpec], list[MessageSpec]] | None:
    """
    Break snippet up into syntactical parts and blocks of code.
    Apply helper functions and get message details.
    Split into overall messages and block-specific messages.

    :param str snippet: code snippet
    :param list snippet_block_els: list of block elements for snippet
    :param xml xml: snippet code as xml object
    :param bool warnings_only: if True, warnings only
    :param bool execute_code: if False, do not execute any code and rely exclusively on AST inspection
    :param set repeat_set: we need to track if a help message is a repeat
     especially across multiple scripts being processed.
    """
    block_specs = get_block_specs(snippet, snippet_block_els)
    overall_snippet_message_specs = get_overall_snippet_message_specs(snippet, block_specs,
        warnings_only=warnings_only, execute_code=execute_code, repeat_set=repeat_set)
    block_level_message_specs = get_block_level_message_specs(block_specs, xml,
        warnings_only=warnings_only, execute_code=execute_code, repeat_set=repeat_set)
    for messages_dets in [overall_snippet_message_specs, block_level_message_specs]:
        if None in messages_dets:
            raise Exception("messages_dets is meant to be a list of MessageDets dataclasses yet a None item was found")
    if not (overall_snippet_message_specs or block_level_message_specs):
        message_level_strs = MessageLevelStrs(conf.NO_ADVICE_MESSAGE, conf.NO_ADVICE_MESSAGE)
        overall_snippet_message_specs = [
            MessageSpec(snippet, message_level_strs, first_line_no=None, warning=False, source=conf.SYSTEM_MESSAGE)]
    return overall_snippet_message_specs, block_level_message_specs

def get_snippet_dets(snippet, *, warnings_only=False, execute_code=True,
        repeat_set=None) -> tuple[tuple[list[MessageSpec], list[MessageSpec]], bool]:
    """
    Get details for snippet of code.

    :return: snippet_messages_dets
     (overall_snippet_messages_dets, block_level_messages_dets),
     multi_block_snippet (bool)
    :rtype: tuple
    """
    tree = get_tree(snippet)
    xml = xml_from_tree(tree)
    if conf.RECORD_AST:
        ast_gen.store_ast_output(xml)
    snippet_block_els = xml.xpath('body')[0].getchildren()  ## [0] because there is only one body under root
    multi_block_snippet = len(snippet_block_els) > 1
    snippet_message_specs = get_separated_message_specs(
        snippet, snippet_block_els, xml, warnings_only=warnings_only, execute_code=execute_code, repeat_set=repeat_set)
    return snippet_message_specs, multi_block_snippet

def get_system_separated_message_specs(snippet, brief_message, *,
        warning=True) -> tuple[list[MessageSpec], list[MessageSpec]]:
    """
    Even though only one message is needed, supplying the details in the
    standard format the displayers expect means they can operate in their usual
    messages_dets consuming ways :-).
    """
    message_level_strs = MessageLevelStrs(brief_message, brief_message)
    overall_messages_spec = [
        MessageSpec(snippet, message_level_strs, first_line_no=None, warning=warning, source=conf.SYSTEM_MESSAGE)]
    block_message_spec = []
    separated_message_specs = (overall_messages_spec, block_message_spec)
    return separated_message_specs

def get_error_message_specs(e, snippet):
    """
    If unable to produce any messages, supply the problem in the form of standard messages_dets
    so the displayers can operate in their usual messages_dets consuming ways :-).
    """
    brief_message = layout(f"""\
        ### No advice sorry :-(

        Unable to provide advice - some sort of problem.

        Details: {e}
        """)
    return get_system_separated_message_specs(snippet, brief_message)

def get_community_message(snippet):
    brief_message = layout("""\

        ### Join in!

        Python has always had a great community. Learn more at
        <https://www.python.org/community/>. Better still - get involved :-)

        """)
    return get_system_separated_message_specs(snippet, brief_message)

def get_xkcd_warning(snippet):
    brief_message = layout("""\

        ### According to XKCD this code could be *very* dangerous

        See <https://xkcd.com/2261/>

        """)
    return get_system_separated_message_specs(snippet, brief_message)
