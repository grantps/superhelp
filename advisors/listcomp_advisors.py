from textwrap import dedent

from advisors import advisor, get_name, get_val, \
    GENERAL_COMPREHENSION_COMMENT, DICT_COMPREHENSION_COMMENT, \
    SET_COMPREHENSION_COMMENT
import conf

@advisor(element_type=conf.LISTCOMP_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def listcomp_overview(element, pre_line_code_str, line_code_str):
    name = get_name(element)
    items = get_val(pre_line_code_str, line_code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list comprehension returning a list
            with {len(items):,} items: {items}
        """),
        conf.EXTRA: (
            dedent(f"""\
            #### Other "comprehensions"

            """)
            + GENERAL_COMPREHENSION_COMMENT
            + dedent("""\


            List comprehensions aren't the only type of comprehension you can
            make. Python also lets you write Dictionary and Set Comprehensions:

            """)
            + DICT_COMPREHENSION_COMMENT
            + '\n\n'
            + SET_COMPREHENSION_COMMENT
            + '\n\n'
            + dedent("""\
            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        ),
    }
    return message
