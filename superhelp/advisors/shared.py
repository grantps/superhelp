import builtins
import keyword
from textwrap import dedent

from ..conf import STD_LIBS
from ..utils import layout_comment as layout

def is_reserved_name(name):
    is_reserved = name in set(keyword.kwlist + dir(builtins) + STD_LIBS)
    return is_reserved

UNPACKING_COMMENT = (
    dedent(f"""\
        Unpacking is much more pythonic than using indexes to pull a sequence
        apart into names (variables). For example:

        """)
    +
    layout(f"""\

        #### Un-pythonic :-(

        location = (-37, 174, 'Auckland', 'Mt Albert')
        lat = location[0]
        lon = location[1]
        city = location[2]
        suburb = location[3]

        #### Pythonic :-)

        lat, lon, city, suburb = location
        """, is_code=True)
    +
    layout(f"""\

        If you don't need all the values you can indicate which you want to
        ignore or even mop up multiple unused values into a single value using
        an asterisk.

        For example:

        """)
    +
    layout(f"""\
        lat, lon, _city, _suburb = location
        """, is_code=True)
    +
    layout(f"""\

        or:

        """)
    +
    layout(f"""\
        lat, lon, *_ = location
        """, is_code=True)
    +
    layout(f"""\

        or:

        """)
    +
    layout(f"""\
        lat, lon, *unused = location
        """, is_code=True)
    +
    layout(f"""\

        Note - unused, in this case, would be ['Auckland', 'Mt Albert']

        """)
)

GENERAL_COMPREHENSION_COMMENT = layout(f"""\
    Comprehensions are one the great things about Python. To see why, have a
    look at Raymond Hettinger's classic talk "Transforming Code into Beautiful,
    Idiomatic Python" <https://youtu.be/OSGv2VnC0go?t=2738> where he explains
    the rationale. In short, if the goal of your code can be expressed as a
    single English sentence then it might belong on one line. The code should
    say what it is doing more than how it is doing it. Comprehensions are
    declarative and that is A Very Good Thing™.

    Pro tip: don't make comprehensions *in*comprehensions ;-). If your
    comprehension is hard to read it is probably better rewritten as a looping
    structure.
    """)

LIST_COMPREHENSION_COMMENT = (
    layout("""\

        #### Example List Comprehension:

        """)
    +
    layout(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        ]
        """, is_code=True)
    +
    layout("""\

        produces an ordinary list:

        """)
    +
    layout(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        ]
        """, is_code=True)
    +
    layout("""\

        produces an ordinary list:

        """)
    +
    layout(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        }
        ))
)

DICT_COMPREHENSION_COMMENT = (
    layout("""\

    #### Example Dictionary Comprehension:

    """)
    +
    layout(f"""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary dictionary:

        """)
    +
    layout(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout(f"""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary dictionary:

        """)
    +
    layout(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }
        ))
)

SET_COMPREHENSION_COMMENT = (
    layout("""\

        #### Example Set Comprehension

        """)
    +
    layout(f"""\
        pets = {{
            pet for _person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout(str(
        {
            pet for _person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }
        ))
    +
    layout("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout(f"""\
        pets = {{
            pet for person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            if person != 'Elliot'
        }}
        """, is_code=True)
    +
    layout("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout(str(
        {
            pet for person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                if person != 'Elliot'
        }
        ))
)
