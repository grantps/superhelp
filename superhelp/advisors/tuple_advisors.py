from ..advisors import filt_block_advisor
from .. import ast_funcs, code_execution, conf, utils
from ..utils import layout_comment

@filt_block_advisor(xpath='body/Assign/value/Tuple')
def tuple_overview(block_dets):
    """
    Explain usage of tuples.
    """
    name = ast_funcs.get_assigned_name(block_dets.element)
    if not name:
        return None
    my_tuple = code_execution.get_val(
        block_dets.pre_block_code_str, block_dets.block_code_str, name)
    if my_tuple:
        tuple_replaced = list(my_tuple)
        tuple_replaced[0] = 100
        tuple_replaced = tuple(tuple_replaced)
        tuple_popped = list(my_tuple)
        tuple_popped.pop()
        tuple_popped = tuple(tuple_popped)
        tuple_appended = list(my_tuple)
        tuple_appended.append(3)
        tuple_appended = tuple(tuple_appended)
        immutability_comment = (f"""
            * cannot be *replaced* -
            so we can't run `{name}`[0] = 100 to get {tuple_replaced}.
            It will raise an exception -
            TypeError: 'tuple' object does not support item assignment)
            * cannot be *removed* -
            so we can't run `{name}`.pop() to get {tuple_popped}.
            * cannot be *added* - so we can't run `{name}`.append(3) to get {tuple_appended}.
            """)
    else:
        immutability_comment = (f"""
            * cannot be *replaced*.
            It will raise an exception -
            TypeError: 'tuple' object does not support item assignment)
            * cannot be *removed*
            * cannot be *added*
            """)
    why_immutability_comment = ("""
            But why would we want a data structure with all those limitations -
            wouldn't a list always be better? In practice it is often useful to
            know that a data structure is not being mutated somewhere inside the
            program. This guarantee makes it easier to reason about what the
            program is doing and what it cannot be doing. We can also use named
            tuples to improve readability.
            """)
    friends = ['Selma', 'Willy', 'Principal Skinner']
    family = ['Bart', 'Lisa', 'Marge', 'Homer']
    original_guests = (friends, family)
    guests = (friends + ['Lenny'], family)
    message = {
        conf.BRIEF: layout_comment(f"""\
            ##### Tuple Overview

            `{name}` is a tuple with {utils.int2nice(len(my_tuple))} items.

            Tuples are like lists but the items inside cannot be replaced,
            removed, or added to. For example, if we have a list [1, 2] we can
            append a 3 to it. But if we have a tuple (1, 2) we cannot.

            {why_immutability_comment}

            Tuples have an order, and can contain duplicate items and items of
            different types (usually not advisable).
            """),
        conf.MAIN: layout_comment(f"""\
            ##### Tuple Overview

            `{name}` is a tuple with {utils.int2nice(len(my_tuple))} items.

            Tuples are like lists but they are immutable.
            That means unchangeable.

            {why_immutability_comment}

            Referring to the tuple `{name}` immutability means that the items
            inside the tuple:

            {immutability_comment}

            Tuples have an order, and can contain duplicate items and items of
            different types (usually not advisable).
            """),
        conf.EXTRA: (
            layout_comment(f"""\

                ##### GOTCHA - immutable means 100% unchangeable right?

                If you have a tuple of mutable data e.g. lists, the content
                of those lists can be altered even while it remains true that you
                can't replace, remove, or add items inside the tuple.

                Demonstration:

                """)
            +
            layout_comment(f"""\
                friends = {friends}
                family = {family}
                guests = (friends, family)

                """, is_code=True)
            +
            layout_comment(f"""\

                `guests` is now {original_guests}. And because `guests` is
                immutable we can't add, remove, or replace its items. But look
                what happens to the `guests` tuple when we append a person to
                friends:

                """)
            +
            layout_comment(f"""\
                friends.append('Lenny')

                """, is_code=True)
            +
            layout_comment(f"""\

                `guests` is now {guests}. An immutable data structure has
                changed! In reality it is the references to individual items
                that are immutable e.g. a reference to the memory address where
                a mutable list sits.

                ##### Named tuples

                Tuples are a light-weight way of defining and storing data. It
                is easier, for example, to write `coord` = (-37, 174) than it is
                to write `coord` = {{'lat': -37, 'lon': 174}}. But it can be
                risky consuming data from tuples in later code if the order or
                number of items changes. What if the tuples you are processing
                change from (lat, lon) to (lon, lat)? References to coord[0]
                would have changed meaning without it being obvious. There can
                be a high risk of bugs.

                Named tuples retain the light-weight advantages of plain vanilla
                tuples but enable us to use a dot notation to reference internal
                items e.g. house_lat = coord.lat. Named tuples also contain
                information on their contents when printed / logged which can
                make debugging much easier.

                Example syntax:

                """)
            +
            layout_comment(f"""\

                from collections import namedtuple
                Coord = namedtuple('Coordinate', 'x, y')
                coord = Coord(-37, 174)
                print(coord)
                # >>> Coordinate(x=-37, y=174))
                """, is_code=True)
            +
            layout_comment(f"""\

                ##### "Tupple" vs "Toople"

                There is no consensus on how to pronounce tuple. Should it rhyme
                with cup or with hoop? People from a more mathematical
                background often prefer "toople". Others prefer to follow the
                spelling and say "tupple".
                """)
        ),
    }
    return message
