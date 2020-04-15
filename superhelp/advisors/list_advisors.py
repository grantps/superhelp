from textwrap import dedent

from ..advisors import filt_block_advisor
from .. import ast_funcs, code_execution, conf, utils
from ..utils import layout_comment

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
@filt_block_advisor(xpath='body/Assign/value/List')
def list_overview(block_dets):
    """
    General overview of list taking content details into account.
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    items = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    item_type_names, _item_type_nice_names = get_item_type_names(items)
    try:
        type4example = item_type_names.pop()
    except IndexError:
        type4example = conf.STR_TYPE
    try:
        example_items = conf.EXAMPLES_OF_TYPES[type4example]
    except KeyError:
        example_items = conf.EXAMPLES_OF_TYPES[conf.STR_TYPE]
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
            layout_comment(f"""\
                {name}.append({listable_example_item})
                """, is_code=True)
            +
            layout_comment(f"""\

                which results in {appended_list}

                """)
            +
            layout_comment("""\

                If you want to add multiple items at once, .extend() is useful.

                Note - we are extending the list which has already had an item
                appended, not the original list.

                """)
            +
            layout_comment(f"""\
                {name}.extend({items2extend})
                """, is_code=True)
            +
            layout_comment(f"""\

                which results in {extended_list}

                """)
            +
            layout_comment("""\
   
                GOTCHA: if you are adding tuples to your list it is easy to
                forget the nested parentheses. E.g.

                """)
            +
            layout_comment(f"""\

                coordinates.append((x, y))  ## Correct

                coordinates.append(x, y)  ## Oops - append only takes one item not two

                """, is_code=True)
            +
            layout_comment("""\

                Lists can also be added together e.g.

                """)
            +
            layout_comment(f"""\
                friends = {friends}
                family = {family}
                guests = friends + family

                """, is_code=True)
            +
            layout_comment(f"""\
   
                resulting in {guests}

                GOTCHA: you can't add individual items to lists unless you put
                them in a list as well E.g.

                """)
            +
            layout_comment(f"""\
                workmate = 'Carl'
                guests = {friends} + {family} + workmate  ## Oops - can only add lists
                guests = {friends} + {family} + [workmate]  ## That's better

                """, is_code=True)
            +
            layout_comment(f"""\

                resulting in {guests + ['Carl']}

                """)
        ),
    }
    return message

@filt_block_advisor(xpath='body/Assign/value/List', warning=True)
def mixed_list_types(block_dets):
    """
    Warns about lists containing a mix of data types.
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    items = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    _item_type_names, item_type_nice_names = get_item_type_names(items)
    if len(item_type_nice_names) <= 1:
        ## No explanation needed if there aren't multiple types.
        return None
    message = {
        conf.BRIEF: layout_comment(f"""
            #### Mix of different data types in list

            `{name}` contains more than one data type - which is probably a bad
            idea.
            """),
        conf.MAIN: layout_comment(f"""
            #### Mix of different data types in list

            `{name}` contains more than one data type - which is probably a bad
            idea. The data types found were: {", ".join(item_type_nice_names)}.
            """),
    }
    return message
