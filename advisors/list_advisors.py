from textwrap import dedent

import advisors
from advisors import type_advisor
import conf, utils

def get_item_type_names(items):
    item_type_names = sorted(set(
        [type(item).__name__ for item in items]
    ))
    item_type_nice_names = [
        conf.TYPE2NAME.get(item_type, item_type)
        for item_type in item_type_names]
    return item_type_names, item_type_nice_names

## only interested in lists when being assigned as a value
## (i.e. <body><Assign><value><List> so we're looking for List under value only)
@type_advisor(element_type=conf.LIST_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def list_overview(line_dets):
    name = advisors.get_assigned_name(line_dets.element)
    items = advisors.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    item_type_names, _item_type_nice_names = get_item_type_names(items)
    try:
        type4example = item_type_names.pop()
    except IndexError:
        type4example = conf.STR_TYPE
    example_items = conf.EXAMPLES_OF_TYPES[type4example]
    example_item = example_items[0]
    listable_example_item = (
        f"'{example_item}'" if type4example == conf.STR_TYPE else example_item)
    appended_list = items.copy()
    appended_list.append(example_item)
    extended_list = appended_list.copy()
    items2extend = example_items[1:3]  ## don't repeat the appended item - might confuse the user at this stage
    extended_list.extend(items2extend)
    friends = ['Selma', 'Willy', 'Principal Skinner']
    family = ['Bart', 'Lisa', 'Marge', 'Homer']
    guests = friends + family
    message = {
        conf.BRIEF: dedent(f"""\
            `{name}` is a list with {utils.int2nice(len(items))} items.

            Lists, along with dictionaries, are the workhorses of Python data
            structures.

            Lists have an order, and can contain duplicate items and items of
            different types (usually not advisable).
            """),
        conf.MAIN: (
            dedent(f"""\
                `{name}` is a list with {utils.int2nice(len(items))} items.
  
                Lists, along with dictionaries, are the workhorses of Python
                data structures.

                Lists have an order, and can contain duplicate items and items
                of different types (usually not advisable).

                Extra items can be added to lists using the .append() method
                e.g.
                """)
            +
            advisors.code_indent(dedent(f"""\
                {name}.append({listable_example_item})
                """))
            +
            dedent(f"""\

                which results in {appended_list}

                """)
            +
            dedent("""\

                If you want to add multiple items at once, .extend() is useful.

                Note - we are extending the list which has already had an item
                appended, not the original list.

                """)
            +
            advisors.code_indent(dedent(f"""\
                {name}.extend({items2extend})
                """))
            +
            dedent(f"""\

                which results in {extended_list}

                """)
            +
            dedent("""\
   
                GOTCHA: if you are adding tuples to your list it is easy to
                forget the nested parentheses. E.g.

                """)
            +
            advisors.code_indent(dedent(f"""\

                coordinates.append((x, y))  ## Correct

                coordinates.append(x, y)  ## Oops - append only takes one item not two

                """))
            +
            dedent("""\

                Lists can also be added together e.g.

                """)
            +
            advisors.code_indent(dedent(f"""\
                friends = {friends}
                family = {family}
                guests = friends + family

                """))
            +
            dedent(f"""\
   
                resulting in {guests}

                GOTCHA: you can't add individual items to lists unless you put
                them in a list as well E.g.

                """)
            +
            advisors.code_indent(dedent(f"""\
                workmate = 'Carl'
                guests = {friends} + {family} + workmate  ## Oops - can only add lists
                guests = {friends} + {family} + [workmate]  ## That's better

                """))
            +
            dedent(f"""\

                resulting in {guests + ['Carl']}

                """)
        ),
    }
    return message

@type_advisor(element_type=conf.LIST_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE, warning=True)
def mixed_list_types(line_dets):
    """
    Warns about lists containing a mix of data types.
    """
    name = advisors.get_assigned_name(line_dets.element)
    items = advisors.get_val(
        line_dets.pre_line_code_str, line_dets.line_code_str, name)
    _item_type_names, item_type_nice_names = get_item_type_names(items)
    if len(item_type_nice_names) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    message = {
        conf.BRIEF: dedent(f"""
            #### Mix of different data types in list
            `{name}` contains more than one data type -
            which is probably a bad idea.
            """),
        conf.MAIN: dedent(f"""
            #### Mix of different data types in list
            `{name}` contains more than one data type -
            which is probably a bad idea. The data types found were:
            {", ".join(item_type_nice_names)}.
            """),
    }
    return message
