from textwrap import dedent

from ..advisors import type_block_advisor
from .. import ast_funcs, code_execution, conf, utils

@type_block_advisor(element_type=conf.FUNC_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE_CALL)
def set_overview(block_dets):
    el = block_dets.element
    name = ast_funcs.get_assigned_name(el)
    if not name:
        return None
    try:
        is_set = el.xpath('value/Call/func/Name')[0].get('id') == 'set'
    except IndexError:
        is_set = False
    if not is_set:
        return None
    my_set = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    empty_set = len(my_set) == 0
    if not empty_set:
        brief_comment = dedent(f"""\
            `{name}` is a set with {utils.int2nice(len(my_set))} members:
            {utils.get_nice_str_list(sorted(my_set), quoter='"')}
            """)
        set_item = list(my_set)[0]
        no_duplicates_demo = (
            dedent(f"""\

            For example:

            """)
            +
            utils.code_indent(dedent(f"""\
                {name}.add({set_item})
                ## >>> {my_set}
                """))
        )
    else:
        brief_comment = dedent(f"""\
            `{name}` is an empty set.
            """)
        no_duplicates_demo = ''
    brief_comment += (
        dedent("""\

            Python sets are brilliant.
            There are often cases in programming where
            you need some sort of set operation
            e.g. you need everything in one set that is not in another.
            In Python you can express that idea directly and semantically
            with set concepts instead of having to build the operations yourself
            in code which needs explaining and testing.

            For example:
        """)
        +
        utils.code_indent(dedent("""\
            people = set(['Sam', 'Avi', 'Terri', 'Noor', 'Hyeji'])
            no_email = set(['Sam', 'Terri'])
            people2email = people - no_email
            ## >>> {'Noor', 'Hyeji', 'Avi'}
            """))
        )
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: (
            brief_comment
            +
            dedent(f"""\

                Being a set, all members are unique by definition
                so if you add something to a set that is already a member
                the set doesn't change.
            """)
            +
            no_duplicates_demo
            +
            dedent("""\

                This is unlike a list which grows each time you append an item
                - the list simply repeats the item. For example:
                """)
            +
            utils.code_indent(dedent("""\
                my_list = [1, 2, 3]
                my_list.append(4)
                my_list.append(4)
                my_list.append(4)
                ## >>> [1, 2, 3, 4, 4, 4]
                my_set = {1, 2, 3}
                my_set.add(4)
                my_set.add(4)
                my_set.add(4)
                ## >>> {1, 2, 3, 4}
                """))
        ),
        conf.EXTRA: (
            dedent("""\
                Set operations can be expressed with operators such as
                '-' (minus) or with methods such as .difference().
    
                Sets are well explained in the official documentation so it will
                suffice to show a simple example.
    
                Note - the operator corresponding to the .union() method is the pipe
                '|' not '+'.
                """)
            +
            utils.code_indent(dedent("""\
                badminton_players = set(['Grant', 'Charlotte', 'Aravind'])
                tennis_players = set(['Giles', 'Grant'])
                squash_players = set(['Grzegorz'])
                racquet_players = badminton_players | tennis_players | squash_players
                ## >>> {'Grzegorz', 'Giles', 'Grant', 'Aravind', 'Charlotte'}
                """))
        )
    }
    return message
