from ..helpers import filt_block_help
from .. import conf
from .. import gen_utils
from ..gen_utils import (
    get_collections_dets, get_nice_str_list, layout_comment as layout)

def truncate_dict(input_dict):
    output_dict = {}
    for k, v in input_dict.items():
        if len(output_dict) >= conf.MAX_ITEMS_EVALUATED:
            break
        output_dict[k] = v
    return output_dict

def get_unknown_status(items):
    if conf.UNKNOWN_ITEM in items:
        return True
    raw_keys = [k for k, _v in items]
    raw_vals = [v for _k, v in items]
    unknowns = (
        items == conf.UNKNOWN_ITEMS
        or conf.UNKNOWN_ITEM in raw_keys
        or conf.UNKNOWN_ITEM in raw_vals)
    return unknowns

ASSIGN_DICT_XPATH = (
    'descendant-or-self::Assign/value/Call/func/Name '
    '| descendant-or-self::Assign/value/Dict')

def get_dict_els(block_el):
    raw_els = block_el.xpath(ASSIGN_DICT_XPATH)
    dict_els = [
        el for el in raw_els if el.tag == 'Dict' or el.get('id') == 'dict']
    return dict_els

def get_comment(names_items, *, brief=True, repeat=False):
    comment_bits = []
    for name, items in names_items:
        empty = len(items) == 0
        unknowns = get_unknown_status(items)
        if unknowns:
            if not repeat:
                comment_bits.append(layout(f"""\

                Unable to evaluate all contents of dictionary `{name}` but still
                able to make some general comments.
                """))
            else:
                comment_bits.append(layout(f"""\
                `{name}` is a dictionary but unable to evaluate contents.
                """))
        elif empty:
            comment_bits.append(layout(f"""\
            `{name}` is an empty dictionary.
            """))
        else:
            plural = '' if len(items) == 1 else 's'
            if brief:
                comment_bits.append(layout(f"""\

                `{name}` is a dictionary with {gen_utils.int2nice(len(items))}
                item{plural} (i.e. {gen_utils.int2nice(len(items))}
                mapping{plural}).
                """))
            else:
                dic = dict(items)  ## safe because no unknowns in this branch
                comment_bits.append(layout(f"""\

                `{name}` is a dictionary with {gen_utils.int2nice(len(dic))}
                item{plural} (i.e. {gen_utils.int2nice(len(dic))}
                mapping{plural}). In this case, the keys are:
                {list(dic.keys())}. We can get the keys using the
                `.keys()` method e.g. `{name}`.`keys()`. The values are
                {list(dic.values())}. We can get the values using the
                `.values()` method e.g. `{name}`.`values()`.
                """))
    comment = ''.join(comment_bits)
    return comment

@filt_block_help(xpath=ASSIGN_DICT_XPATH)
def dict_overview(block_dets, *, repeat=False, execute_code=True, **_kwargs):
    """
    Look at assigned dictionaries e.g. location = {'country' 'New Zealand',
    'city': 'Auckland'}
    """
    dict_els = get_dict_els(block_dets.element)
    if not dict_els:
        return None
    plural = 'ies' if len(dict_els) > 1 else 'y'
    title = layout(f"""\
    ### Dictionar{plural} defined
    """)
    names_items, oversized_msg = get_collections_dets(dict_els, block_dets,
        collection_plural='dictionaries', truncated_items_func=truncate_dict,
        execute_code=execute_code)
    brief_desc = get_comment(names_items, repeat=repeat)
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
        first_name = None
        main_dict_desc = get_comment(names_items, brief=False, repeat=repeat)
        for name, items in names_items:
            unknowns = get_unknown_status(items)
            if not first_name and not unknowns:
                first_name = name
        if first_name is None:
            first_name = 'demo_dict'
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
        are by the mighty Brandon Rhodes:

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
        [type(k).__name__ for k, _v in items]
    ))
    key_type_nice_names = [
        conf.TYPE2NAME.get(key_type, key_type)
        for key_type in key_type_names]
    return key_type_names, key_type_nice_names

@filt_block_help(xpath=ASSIGN_DICT_XPATH, warning=True)
def mixed_key_types(block_dets, *, repeat=False, execute_code=True, **_kwargs):
    """
    Warns about dictionaries with mix of string and integer keys.
    """
    dict_els = get_dict_els(block_dets.element)
    if not dict_els:
        return None
    mixed_names = []
    names_items, oversized_msg = get_collections_dets(dict_els, block_dets,
        collection_plural='dictionaries', truncated_items_func=truncate_dict,
        execute_code=execute_code)
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
