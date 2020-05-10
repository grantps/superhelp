from ..advisors import filt_block_advisor
from .. import code_execution, conf, utils
from ..utils import layout_comment as layout

def truncate_tuple(items):
    return tuple(items[: conf.MAX_ITEMS_EVALUATED])

ASSIGN_TUPLE_XPATH = 'descendant-or-self::Assign/value/Tuple'

@filt_block_advisor(xpath=ASSIGN_TUPLE_XPATH)
def tuple_overview(block_dets, *, repeat=False):
    """
    Explain usage of tuples.
    """
    tup_els = block_dets.element.xpath(ASSIGN_TUPLE_XPATH)
    names_items, oversized_msg = code_execution.get_collections_dets(
        tup_els, block_dets,
        collection_plural='tuples', truncated_items_func=truncate_tuple)
    assigned_names_items = [
        (name, items) for name, items in names_items if name]
    if not assigned_names_items:
        return None

    title = layout("""\
    #### Tuple Overview
    """)
    summary_bits = []
    for name, tup in assigned_names_items:
        if tup:
            summary_bits.append(layout(f"""\
            `{name}` is a tuple. Unable to evaluate items.
            """))
        else:
            summary_bits.append(layout(f"""\
            `{name}` is a tuple with {utils.int2nice(len(tup))} items.
            """))
    summary = ''.join(summary_bits)
    if not repeat:
        quick_immutability = layout("""\

        Tuples are like lists but the items inside cannot be replaced, removed,
        or added to. For example, if we have a list [1, 2] we can append a 3 to
        it. But if we have a tuple (1, 2) we cannot.
        """)
        pre_immutability = layout("""\

        Tuples are like lists but they are immutable. That means unchangeable.
        """)
        why_immutability = layout("""\

        But why would we want a data structure with all those limitations -
        wouldn't a list always be better? In practice it is often useful to know
        that a data structure is not being mutated somewhere inside the program.
        This guarantee makes it easier to reason about what the program is doing
        and what it cannot be doing. We can also use named tuples to improve
        readability.
        """)
        ordered = layout("""\

        Tuples have an order, and can contain duplicate items and items of
        different types (usually not advisable).
        """)
        non_empty_name_tups = [
            (name, tup) for name, tup in assigned_names_items if tup]
        immutability_question = ("So what is tuple immutability in practice? "
            "It means that tuple items:")
        if non_empty_name_tups:
            first_name, first_tup = non_empty_name_tups[0]
            tup_replaced = list(first_tup)
            tup_replaced[0] = 100
            tup_replaced = tuple(tup_replaced)
            tup_popped = list(first_tup)
            tup_popped.pop()
            tup_popped = tuple(tup_popped)
            tup_appended = list(first_tup)
            tup_appended.append(3)
            tup_appended = tuple(tup_appended)
            longer_immutability = layout(f"""
            {immutability_question}

            * cannot be *replaced* - so we can't run `{first_name}`[0] = 100 to
            get {tup_replaced}. It will raise an exception - TypeError:
            'tuple' object does not support item assignment)

            * cannot be *removed* - so we can't run `{first_name}`.pop() to get
            {tup_popped}.

            * cannot be *added* - so we can't run `{name}`.append(3) to get
            {tup_appended}.
            """)
        else:
            longer_immutability = layout(f"""
            {immutability_question}

            * cannot be *replaced*. It will raise an exception - TypeError:
            'tuple' object does not support item assignment)

            * cannot be *removed*

            * cannot be *added*
            """)
        friends = ['Selma', 'Willy', 'Principal Skinner']
        family = ['Bart', 'Lisa', 'Marge', 'Homer']
        original_guests = (friends, family)
        guests = (friends + ['Lenny'], family)
        extra = (
            layout("""\
            #### GOTCHA - immutable means 100% unchangeable right?

            If you have a tuple of mutable data e.g. lists, the content of those
            lists can be altered even while it remains true that you can't
            replace, remove, or add items inside the tuple.

            Demonstration:
            """)
            +
            layout(f"""\
            friends = {friends}
            family = {family}
            guests = (friends, family)
            """, is_code=True)
            +
            layout(f"""\

            `guests` is now {original_guests}. And because `guests` is immutable
            we can't add, remove, or replace its items. But look what happens to
            the `guests` tuple when we append a person to friends:
            """)
            +
            layout(f"""\
            friends.append('Lenny')
            """, is_code=True)
            +
            layout(f"""\

            `guests` is now {guests}. An immutable data structure has changed!
            In reality it is the references to individual items that are
            immutable e.g. a reference to the memory address where a mutable
            list sits.

            #### Named tuples

            Tuples are a light-weight way of defining and storing data. It is
            easier, for example, to write `coord` = (-37, 174) than it is to
            write `coord` = {{'lat': -37, 'lon': 174}}. But it can be risky
            consuming data from tuples in later code if the order or number of
            items changes. What if the tuples you are processing change from
            (lat, lon) to (lon, lat)? References to coord[0] would have changed
            meaning without it being obvious. There can be a high risk of bugs.

            Named tuples retain the light-weight advantages of plain vanilla
            tuples but enable us to use a dot notation to reference internal
            items e.g. house_lat = coord.lat. Named tuples also contain
            information on their contents when printed / logged which can make
            debugging much easier.

            Example syntax:
            """)
            +
            layout(f"""\
            from collections import namedtuple
            Coord = namedtuple('Coordinate', 'x, y')
            coord = Coord(-37, 174)
            print(coord)
            # >>> Coordinate(x=-37, y=174))
            """, is_code=True)
            +
            layout(f"""\
            #### "Tupple" vs "Toople"

            There is no consensus on how to pronounce tuple. Should it rhyme
            with cup or with hoop? People from a more mathematical background
            often prefer "toople". Others prefer to follow the spelling and say
            "tupple".
            """)
        )
    else:
        quick_immutability = ''
        pre_immutability = ''
        why_immutability = ''
        ordered = ''
        longer_immutability = ''
        extra = ''

    message = {
        conf.BRIEF: (title + oversized_msg + summary + quick_immutability
            + why_immutability + ordered),
        conf.MAIN: (title + oversized_msg + summary + pre_immutability
            + why_immutability + longer_immutability + ordered),
        conf.EXTRA: extra,
    }
    return message
