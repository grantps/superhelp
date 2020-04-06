from textwrap import dedent

import advisors
from advisors import type_advisor
import conf, utils

@type_advisor(element_type=conf.DICT_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def dict_overview(line_dets):
    name = advisors.get_name(line_dets.element)
    items = advisors.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    if not items:
        return None
    message = {
        conf.BRIEF: dedent(f"""
            Dictionaries map keys to values.
            `{name}` is a dictionary with {utils.int2nice(len(items))}
            items (i.e. {utils.int2nice(len(items))} mappings)

            Keys are unique but values can be repeated.

            Dictionaries, along with lists, are the workhorses of Python
            data structures.
        """),
        conf.MAIN: (
            dedent(f"""
                Dictionaries, along with lists, are the workhorses of Python
                data structures.

                Dictionaries map keys to values.
                `{name}` is a dictionary with {utils.int2nice(len(items))}
                items (i.e. {utils.int2nice(len(items))} mappings)

                In this case, the keys are: {list(items.keys())}
                (we can get the keys using the .keys() method
                e.g. `{name}`.keys())
                and the values are {list(items.values())}
                (we can get the values using the .values() method
                e.g. `{name}`.values())

                It is common to iterate through the key-value pairs of a
                dictionary.
                This can be achieved using the dictionary's .items() method. E.g.

                """)
            +
            advisors.code_indent(dedent(f"""\
                ## k, v is conventional, and OK in a hurry, but readable names
                ## are probably better for code you're going to maintain
                for k, v in {name}.items():
                    print(f"key {{k}} maps to value {{v}}")
                """))
            +
            dedent(f"""
                
                Keys are unique but values can be repeated. For example:

                """)
            +
            advisors.code_indent(dedent(f"""
                country2car = {{'Japan': 'Toyota', 'Sweden': 'Volvo'}}  ## OK - all keys are unique
                country2car = {{'Japan': 'Toyota', 'Japan': 'Honda'}}  ## Oops - the 'Japan' key is repeated

                """))
            +
            dedent(f"""

                In which case a better structure might be to have each 'value'
                being a list e.g.

                """)
            +
            advisors.code_indent(dedent(f"""
                country2cars = {{'Japan': ['Toyota', 'Honda'], 'Sweden': ['Volvo']}}  ## OK - all keys are unique

                """))
        ),
        conf.EXTRA: dedent("""\

            Python dictionaries (now) keep the order in which items are added.

            They are also super-efficient and fast. The two presentations to
            watch are by living treasure Brandon Rhodes:

            1. The Dictionary Even Mightier - <https://www.youtube.com/watch?v=66P5FMkWoVU>
            1. The Mighty Dictionary - <https://www.youtube.com/watch?v=oMyy4Sm0uBs>
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

@type_advisor(
    element_type=conf.DICT_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE, warning=True)
def mixed_list_types(line_dets):
    """
    Warns about dictionaries with mix of string and integer keys.
    """
    name = advisors.get_name(line_dets.element)
    items = advisors.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    key_type_names, _key_type_nice_names = get_key_type_names(items)
    bad_key_type_combo = (
        conf.INT_TYPE in key_type_names and conf.STR_TYPE in key_type_names)
    if not bad_key_type_combo:
        return None
    message = {
        conf.BRIEF: dedent(f"""
            #### Mix of integer and string keys in dictionary
            `{name}`'s keys include both strings and integers
            which is probably a bad idea.
            """),
        conf.MAIN: dedent(f"""
            #### Mix of integer and string keys in dictionary
            `{name}`'s keys include both strings and integers
            which is probably a bad idea.

            For example, if you have both 1 and "1" as keys in a dictionary
            (which is allowed because they are not the same key) it is very easy
            to get confused and create Hard To Find™ bugs. You _might_ not
            regret it but you probably will ;-).
            """),
    }
    return message
