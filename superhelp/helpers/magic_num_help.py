from .. import conf
from ..ast_funcs import num_str_from_parent_el
from ..gen_utils import get_nice_str_list, layout_comment as layout
from ..helpers import any_block_help

@any_block_help(warning=True)
def magic_number(block_dets, *, repeat=False, **_kwargs):
    """
    Warn about magic numbers - suggest "constants" or Enums.
    """
    comparator_els = block_dets.element.xpath('descendant-or-self::comparators')
    if not comparator_els:
        return None
    num_strs = []
    for comparator_el in comparator_els:
        num_str = num_str_from_parent_el(comparator_el)
        if num_str:
            num_strs.append(num_str)
    if not num_strs:
        return None
    magic_num_strs = sorted(set(num_strs) - set(conf.NON_MAGIC_NUM_STRS))
    if not magic_num_strs:
        return None

    title = layout("""\
    ### Magic numbers possibly found
    """)
    magic_strs = get_nice_str_list(magic_num_strs)
    brief_comment = layout(f"""\
    Found the following "magic" number(s): {magic_strs}
    """)
    if not repeat:
        main_explanation = (
            layout("""\

            Magic numbers are numbers which mean something specific but the
            meaning is not made obvious in the code. To illustrate, which code
            is easier to understand? The snippet using magic number 86_400:
            """)
            +
            layout("""\
            while seconds < 86_400:
                pass
            """, is_code=True)
            +
            layout("""\
            or the snippet using "constant" SECONDS_IN_DAY, which has an obvious
            meaning:
            """)
            +
            layout("""\
            while seconds < SECONDS_IN_DAY:
                pass
            """, is_code=True)
            + layout("""\

            Named constants are much more semantic i.e. readable. They clearly
            express their meaning.

            A constant is a value which is fixed throughout the program e.g.
            SCREEN_WIDTH, PI, or GRAVITY. Note - Python doesn't really have
            constants as such but it is conventional to use SCREAMING_SNAKE_CASE
            (capitals joined by underscores) to indicate a variable should be
            treated as a constant.

            Magic numbers make it hard to understand the code. They certainly
            make it more difficult to maintain and develop in the future when
            the original intentions of the coder have been forgotten. A new
            person working on the code might be wondering if there is a
            relationship between the same number appearing in different places.
            Is it safe to change them? And is it OK to change it in one place
            without also changing it in another?

            For example, in one context 52 might refer to the number of cards in
            a card deck; in another 52 might refer to the number of weeks in a
            Gregorian calendar. The two meanings should be kept distinct. See
            <https://en.wikipedia.org/wiki/Magic_number_(programming)>

            Magic numbers can also be typo risks. Was it 84_600 in the previous
            example or 86_400?

            The solution is to declare variables which name the special values
            e.g. SECONDS_IN_DAY = 86_400
            """)
        )
        extra = (
            layout("""\
            If multiple numbers have specific meaning it might make sense to
            create an Enum but be warned, the plain vanilla Enum doesn't allow
            comparisons with non-enums.

            An example use of an IntEnum:
            """)
            +
            layout("""\
            import enum


            class Pieces(enum.IntEnum):  ## note - using IntEnum to allow non-enum comparisons

                PAWN = 8
                ROOK = 2
                BISHOP = 2
                KNIGHT = 2
                KING = 1
                QUEEN = 1


            n_pieces = 2
            if n_pieces == Pieces.KNIGHT:  ## comparison between integer (non-enum) and IntEnum
                pass
            """, is_code=True)
        )
    else:
        main_explanation = ''
        extra = ''

    message = {
        conf.Level.BRIEF: title + brief_comment,
        conf.Level.MAIN: title + brief_comment + main_explanation,
        conf.Level.EXTRA: extra,
    }
    return message
