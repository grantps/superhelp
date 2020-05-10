from ..advisors import filt_block_advisor
from .. import code_execution, conf, utils
from ..utils import layout_comment as layout

def truncate_set(items):
    return set(list(items)[: conf.MAX_ITEMS_EVALUATED])

ASSIGN_FUNC_NAME_XPATH = 'descendant-or-self::Assign/value/Call/func/Name'

@filt_block_advisor(xpath=ASSIGN_FUNC_NAME_XPATH)
def set_overview(block_dets, *, repeat=False):
    """
    Look for sets and provide general advice on using them and finding out more.
    """
    func_type_els = block_dets.element.xpath(ASSIGN_FUNC_NAME_XPATH)
    set_els = [func_type_el for func_type_el in func_type_els
        if func_type_el.get('id') == 'set']
    names_items, oversized_msg = code_execution.get_collections_dets(
        set_els, block_dets,
        collection_plural='sets', truncated_items_func=truncate_set)
    name_sets = [
        (name, items) for name, items in names_items if items is not None]
    if not name_sets:
        return None

    title = layout("""\
    ### Set details
    """)
    summary_bits = []
    for name, my_set in name_sets:
        empty_set = len(my_set) == 0
        if empty_set:
            summary_bits.append(layout(f"""\
            `{name}` is an empty set.
            """))
        else:
            members = str(sorted(my_set)).strip('[').strip(']')
            summary_bits.append(layout(f"""\

            `{name}` is a set with {utils.int2nice(len(my_set))} members:
            {members}
            """))
    summary = ''.join(summary_bits)
    if not repeat:
        sets_rock = (
            layout("""\

            Python sets are brilliant. There are often cases in programming
            where you need some sort of set operation e.g. you need everything
            in one set that is not in another. In Python you can express that
            idea directly and semantically with set concepts instead of having
            to build the operations yourself in code which needs explaining and
            testing.

            For example:
            """)
            +
            layout("""\
            people = set(['Sam', 'Avi', 'Terri', 'Noor', 'Hyeji'])
            no_email = set(['Sam', 'Terri'])
            people2email = people - no_email
            ## >>> {'Noor', 'Hyeji', 'Avi'}
            """, is_code=True)
        )
        no_duplicates_demo = ''
        for name, my_set in name_sets:
            empty_set = len(my_set) == 0
            if not empty_set:
                members = str(sorted(my_set)).strip('[').strip(']')
                existing_set_item = list(my_set)[0]
                no_duplicates_demo = (
                    layout("""\
                    For example:
                    """)
                    +
                    layout(f"""\
                    {name}.add({existing_set_item})
                    ## >>> {my_set}
                    """, is_code=True)
                )
                break
        set_dets = (
            layout(f"""\

            Being a set, all members are unique by definition so if you add
            something to a set that is already a member the set doesn't change.
            """)
            +
            no_duplicates_demo
            +
            layout("""\

            This is unlike a list which grows each time you append an item - the
            list simply repeats the item. For example:
            """)
            +
            layout("""\
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
            """, is_code=True)
        )
        set_extras = (
            layout("""\

            Set operations can be expressed with operators such as `-` (minus)
            or with methods such as .difference().

            Sets are well explained in the official documentation so it will
            suffice to show a simple example.

            Note - the operator corresponding to the `.union()` method is the
            pipe `|` not `+`.
            """)
            +
            layout("""\
            badminton_players = set(['Grant', 'Charlotte', 'Aravind'])
            tennis_players = set(['Giles', 'Grant'])
            squash_players = set(['Grzegorz'])
            racquet_players = badminton_players | tennis_players | squash_players
            ## >>> {'Grzegorz', 'Giles', 'Grant', 'Aravind', 'Charlotte'}
            """, is_code=True)
        )
    else:
        sets_rock = ''
        set_dets = ''
        set_extras = ''

    message = {
        conf.BRIEF: title + oversized_msg + summary + sets_rock,
        conf.MAIN: title + oversized_msg + summary + sets_rock + set_dets,
        conf.EXTRA: set_extras,
    }
    return message
