from textwrap import dedent

import advisors
from advisors import advisor
import conf, utils


@advisor(element_type=conf.TUPLE_ELEMENT_TYPE,
    xml_root=conf.XML_ROOT_BODY_ASSIGN_VALUE)
def tuple_overview(element, std_imports, code_str):
    name = advisors.get_name(element)
    my_tuple = advisors.get_val(std_imports, code_str, name)
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
        conf.BRIEF: dedent(f"""\
            `{name}` is a tuple with {utils.int2nice(len(my_tuple))} items.

            Tuples are like lists but the items inside cannot be replaced,
            removed, or added to. For example, if we have a list [1, 2] we can
            append a 3 to it. But if we have a tuple (1, 2) we cannot.

            {why_immutability_comment}

            Tuples have an order, and can contain duplicate items and items of
            different types (usually not advisable).
            """),
        conf.MAIN: dedent(f"""\
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
            dedent(f"""\

                GOTCHA - if you have a tuple of mutable data e.g. lists, the content
                of those lists can be altered even while it remains true that you
                can't replace, remove, or add items inside the tuple.

                Demonstration:

                """)
            +
            advisors.code_indent(dedent(f"""\
                friends = {friends}
                family = {family}
                guests = (friends, family)

                """))
            +
            dedent(f"""\

                `guests` is now {original_guests}. And because `guests` is
                immutable we can't add, remove, or replace its items. But look
                what happens to the `guests` tuple when we append a person to
                friends:

                """)
            +
            advisors.code_indent(dedent(f"""\
                friends.append('Lenny')

                """))
            +
            dedent(f"""\

                `guests` is now {guests}. An immutable data structure has
                changed! In reality it is the references to individual items
                that are immutable e.g. a reference to the memory address where
                a mutable list sits.

                """)
        ),
    }
    return message
