from ..advisors import filt_block_advisor
from .. import code_execution, conf, utils
from ..utils import get_nice_str_list, layout_comment as layout

def truncate_dict(input_dict):
    output_dict = {}
    for k, v in input_dict.items():
        if len(output_dict) >= conf.MAX_ITEMS_EVALUATED:
            break
        output_dict[k] = v
    return output_dict

ASSIGN_DICT_XPATH = 'descendant-or-self::Assign/value/Dict'

@filt_block_advisor(xpath=ASSIGN_DICT_XPATH)
def dict_overview(block_dets, *, repeat=False):
    """
    Look at assigned dictionaries e.g. location = {'country' 'New Zealand',
    'city': 'Auckland'}
    """
    dict_els = block_dets.element.xpath(ASSIGN_DICT_XPATH)
    plural = 'ies' if len(dict_els) > 1 else 'y'
    title = layout(f"""\
    ### Dictionar{plural} defined
    """)
    brief_desc_bits = []
    names_items, oversized_msg = code_execution.get_collections_dets(
        dict_els, block_dets,
        collection_plural='dictionaries', truncated_items_func=truncate_dict)
    for name, items in names_items:
        if items is None:
            brief_desc_bits.append(layout(f"""\
            `{name}` is a dictionary. Unable to evaluate items.
            """))
        else:
            brief_desc_bits.append(layout(f"""\

            `{name}` is a dictionary with {utils.int2nice(len(items))} items
            (i.e. {utils.int2nice(len(items))} mappings).
            """))
    brief_desc = ''.join(brief_desc_bits)
    if not repeat:
        dict_def = layout("""\
        Dictionaries map keys to values.
        """)
        workhorses = layout("""\

        Dictionaries, along with lists, are the workhorses of Python data
        structures.
        """)
        keys_and_vals = layout("""\
        Keys are unique but values can be repeated.
        """)
        dict_desc_bits = []
        first_name = None
        for name, items in names_items:
            if not items:
                dict_desc_bits.append(layout(f"""\
                `{name}` is a dictionary. Unable to evaluate items.
                """))
            else:
                if not first_name:
                    first_name = name
                empty_dict = (len(items) == 0)
                if empty_dict:
                    dict_desc_bits.append(layout(f"""\
                    `{name}` is an empty dictionary.
                    """))
                else:
                    plural = '' if len(items) == 1 else 's'
                    dict_desc_bits.append(layout(f"""\

                    `{name}` is a dictionary with {utils.int2nice(len(items))}
                    item{plural} (i.e. {utils.int2nice(len(items))}
                    mapping{plural}). In this case, the keys are:
                    {list(items.keys())}. We can get the keys using the
                    `.keys()` method e.g. `{name}`.`keys()`. The values are
                    {list(items.values())}. We can get the values using the
                    `.values()` method e.g. `{name}`.`values()`.
                    """))
        if first_name is None:
            first_name = 'demo_dict'
        main_dict_desc = ''.join(dict_desc_bits)
        general = (
            layout(f"""

            It is common to iterate through the key-value pairs of a dictionary.
            This can be achieved using the dictionary's `.items()` method. E.g.
            """)
            +
            layout(f"""\

            ## k, v is conventional, and OK in a hurry, but readable names
            ## are probably better for code you're going to maintain
            for k, v in {first_name}.items():
                print(f"key {{k}} maps to value {{v}}")
            """, is_code=True)
            +
            layout("""
            Keys are unique but values can be repeated. For example:
            """)
            +
            layout(f"""
            country2car = {{'Japan': 'Toyota', 'Sweden': 'Volvo'}}  ## OK - all keys are unique
            country2car = {{'Japan': 'Toyota', 'Japan': 'Honda'}}  ## Oops - the 'Japan' key is repeated
            """, is_code=True)
            +
            layout(f"""

            In which case a better structure might be to have each 'value' being
            a list e.g.
            """)
            +
            layout(f"""
            country2cars = {{'Japan': ['Toyota', 'Honda'], 'Sweden': ['Volvo']}}  ## OK - all keys are unique
            """, is_code=True)
        )
        mighty_dict = layout("""\

        Python dictionaries (now) keep the order in which items are added.

        They are also super-efficient and fast. The two presentations to watch
        are by living treasure Brandon Rhodes:

        1. The Dictionary Even Mightier -
        <https://www.youtube.com/watch?v=66P5FMkWoVU>
        2. The Mighty Dictionary - <https://www.youtube.com/watch?v=oMyy4Sm0uBs>
        """)
    else:
        dict_def = ''
        workhorses = ''
        keys_and_vals = ''
        main_dict_desc = brief_desc
        general = ''
        mighty_dict = ''

    message = {
        conf.BRIEF: (title + oversized_msg + dict_def + brief_desc
            + keys_and_vals + workhorses),
        conf.MAIN: (
            title + oversized_msg + main_dict_desc + workhorses + general),
        conf.EXTRA: mighty_dict,
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
def mixed_key_types(block_dets, *, repeat=False):
    """
    Warns about dictionaries with mix of string and integer keys.
    """
    dict_els = block_dets.element.xpath(ASSIGN_DICT_XPATH)
    mixed_names = []
    names_items, oversized_msg = code_execution.get_collections_dets(
        dict_els, block_dets,
        collection_plural='dictionaries', truncated_items_func=truncate_dict)
    for name, items in names_items:
        if not items:
            continue
        key_type_names, _key_type_nice_names = get_key_type_names(items)
        bad_key_type_combo = (
            conf.INT_TYPE in key_type_names and conf.STR_TYPE in key_type_names)
        if not bad_key_type_combo:
            continue
        mixed_names.append(name)
    if not mixed_names:
        return None

    title = layout("""\
    ### Mix of integer and string keys in dictionary
    """)
    multiple = len(mixed_names) > 1
    if multiple:
        nice_str_list = get_nice_str_list(mixed_names, quoter='`')
        mixed_warning = layout(f"""

        {nice_str_list} have keys include a mix of strings and integers - which
        is probably a bad idea.
        """)
    else:
        mixed_warning = layout(f"""

        `{name}`'s keys include both strings and integers which is probably a
        bad idea.
        """)
    if not repeat:
        one_vs_1 = layout("""\

        For example, if you have both 1 and "1" as keys in a dictionary (which
        is allowed because they are not the same key) it is very easy to get
        confused and create Hard To Find™ bugs. You _might_ not regret it but
        you probably will ;-).
        """)
    else:
        one_vs_1 = ''

    message = {
        conf.BRIEF: title + oversized_msg + mixed_warning,
        conf.MAIN: title + oversized_msg + mixed_warning + one_vs_1,
    }
    return message
