from ..advisors import filt_block_advisor
from .. import code_execution, conf, utils
from ..ast_funcs import get_assign_name
from ..utils import layout_comment

ASSIGN_DICT_XPATH = 'descendant-or-self::Assign/value/Dict'

def _get_additional_main_comment(first_name):
    additional_main_comment = (
        layout_comment(f"""

            It is common to iterate through the key-value pairs of a dictionary.
            This can be achieved using the dictionary's .items() method. E.g.

            """)
        +
        layout_comment(f"""\
            ## k, v is conventional, and OK in a hurry, but readable names
            ## are probably better for code you're going to maintain
            for k, v in {first_name}.items():
                print(f"key {{k}} maps to value {{v}}")
            """, is_code=True)
        +
        layout_comment(f"""
            
            Keys are unique but values can be repeated. For example:

            """)
        +
        layout_comment(f"""
            country2car = {{'Japan': 'Toyota', 'Sweden': 'Volvo'}}  ## OK - all keys are unique
            country2car = {{'Japan': 'Toyota', 'Japan': 'Honda'}}  ## Oops - the 'Japan' key is repeated

            """, is_code=True)
        +
        layout_comment(f"""

            In which case a better structure might be to have each 'value'
            being a list e.g.

            """)
        +
        layout_comment(f"""
            country2cars = {{'Japan': ['Toyota', 'Honda'], 'Sweden': ['Volvo']}}  ## OK - all keys are unique

            """, is_code=True)
    )
    return additional_main_comment

@filt_block_advisor(xpath=ASSIGN_DICT_XPATH)
def dict_overview(block_dets):
    """
    Look at assigned dictionaries e.g. location = {'country' 'New Zealand',
    'city': 'Auckland'}
    """
    dict_els = block_dets.element.xpath(ASSIGN_DICT_XPATH)
    brief_comment = ''
    main_comment = ''
    plural = 'ies' if len(dict_els) > 1 else 'y'
    first_name = None
    for i, dict_el in enumerate(dict_els):
        first = (i == 0)
        name = get_assign_name(dict_el)
        items = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        if first:
            first_name = name
            title = layout_comment(f"""\

                #### Dictionar{plural} defined

                """)
            brief_comment += title
            main_comment += title
        
        brief_comment += layout_comment("""\

            Dictionaries map keys to values.

            """)
        main_comment += layout_comment("""\

            Dictionaries, along with lists, are the workhorses of Python data
            structures.

            """)

        list_desc = layout_comment(f"""\

            `{name}` is a dictionary with
            {utils.int2nice(len(items))} items (i.e.
            {utils.int2nice(len(items))} mappings)

            In this case, the keys are: {list(items.keys())}. We can
            get the keys using the .keys() method e.g. `{name}`.keys().
            The values are {list(items.values())}. We can get the
            values using the .values() method e.g. `{name}`.values().

            """)
        brief_comment += list_desc
        main_comment += list_desc
   
        brief_comment += layout_comment("""\

            Keys are unique but values can be repeated.

            Dictionaries, along with lists, are the workhorses of Python data
            structures.
            """)
        main_comment += _get_additional_main_comment(first_name)
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: main_comment,
        conf.EXTRA: layout_comment("""\

            Python dictionaries (now) keep the order in which items are added.

            They are also super-efficient and fast. The two presentations to
            watch are by living treasure Brandon Rhodes:

            1. The Dictionary Even Mightier -
            <https://www.youtube.com/watch?v=66P5FMkWoVU>
            2. The Mighty Dictionary -
            <https://www.youtube.com/watch?v=oMyy4Sm0uBs>
            """)
    }
    return message

def get_key_type_names(items):
    key_type_names = sorted(set(
        [type(item).__name__ for item in items]
    ))
    key_type_nice_names = [
        conf.TYPE2NAME.get(key_type, key_type)
        for key_type in key_type_names]
    return key_type_names, key_type_nice_names

@filt_block_advisor(xpath=ASSIGN_DICT_XPATH, warning=True)
def mixed_key_types(block_dets):
    """
    Warns about dictionaries with mix of string and integer keys.
    """
    dict_els = block_dets.element.xpath(ASSIGN_DICT_XPATH)
    brief_comment = ''
    main_comment = ''
    has_mixed = False
    for i, dict_el in enumerate(dict_els):
        first = (i == 0)
        name = get_assign_name(dict_el)
        items = code_execution.get_val(
            block_dets.pre_block_code_str, block_dets.block_code_str, name)
        key_type_names, _key_type_nice_names = get_key_type_names(items)
        bad_key_type_combo = (
            conf.INT_TYPE in key_type_names and conf.STR_TYPE in key_type_names)
        if not bad_key_type_combo:
            continue
        has_mixed = True
        if first:
            title = layout_comment(f"""\

                #### Mix of integer and string keys in dictionary

                """)
            brief_comment += title
            main_comment += title 
        mixed_warning = layout_comment(f"""

            `{name}`'s keys include both strings and integers which is probably
            a bad idea.
            """)
        brief_comment += mixed_warning
        main_comment += mixed_warning
        main_comment += layout_comment("""\

            For example, if you have both 1 and "1" as keys in a dictionary
            (which is allowed because they are not the same key) it is very easy
            to get confused and create Hard To Find™ bugs. You _might_ not
            regret it but you probably will ;-).            
            """)

    if not has_mixed:
        return None
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: main_comment,
    }
    return message
