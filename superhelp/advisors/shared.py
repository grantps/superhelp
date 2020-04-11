from textwrap import dedent

from ..utils import layout_comment

UNPACKING_COMMENT = (
    dedent(f"""\
        Unpacking is much more pythonic than using indexes to pull a
        sequence apart into names (variables). For example:

        """)
    +
    layout_comment(f"""\
        ##### Un-pythonic :-(

        location = (-37, 174, 'Auckland', 'Mt Albert')
        lat = location[0]
        lon = location[1]
        city = location[2]
        suburb = location[3]

        ##### Pythonic :-)
        lat, lon, city, suburb = location
        """, is_code=True)
    +
    layout_comment(f"""\

        If you don't need all the values you can indicate which you want
        to ignore or even mop up multiple unused values into a single
        value using an asterisk. 

        For example:

        """)
    +
    layout_comment(f"""\
        lat, lon, _city, _suburb = location
        """, is_code=True)
    +
    layout_comment(f"""\

        or:

        """)
    +
    layout_comment(f"""\
        lat, lon, *_ = location
        """, is_code=True)
    +
    layout_comment(f"""\

        or:

        """)
    +
    layout_comment(f"""\
        lat, lon, *unused = location
        """, is_code=True)
    +
    layout_comment(f"""\

        Note - unused, in this case, would be ['Auckland', 'Mt Albert']

        """)
)

GENERAL_COMPREHENSION_COMMENT = layout_comment(f"""\
    Comprehensions are one the great things about Python. To see why,
    have a look at Raymond Hettinger's classic talk "Transforming Code
    into Beautiful, Idiomatic Python"
    <https://youtu.be/OSGv2VnC0go?t=2738> where he explains the
    rationale. In short, if the goal of your code can be expressed as a
    single English sentence then it might belong on one line. The code
    should say what it is doing more than how it is doing it.
    Comprehensions are declarative and that is A Very Good Thing™.

    Pro tip: don't make comprehensions *in*comprehensions ;-).
    If your comprehension is hard to read it is probably better rewritten as a
    looping structure.
    """)

LIST_COMPREHENSION_COMMENT = (
    layout_comment("""\
        ##### Example List Comprehension:
        """)
    +
    layout_comment(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        ]
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary list:

        """)
    +
    layout_comment(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
        }
        ))
    +
    layout_comment("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout_comment(f"""\
        names_lengths = [
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        ]
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary list:

        """)
    +
    layout_comment(str(
        {
            len(name)
            for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            if not name.startswith('T')
        }
        ))
)

DICT_COMPREHENSION_COMMENT = (
    layout_comment("""\
    ##### Example Dictionary Comprehension:
    """)
    +
    layout_comment(f"""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }}
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary dictionary:

        """)
    +
    layout_comment(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
        }
        ))
    +
    layout_comment("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout_comment(f"""\
        country2capital = {{
            country: capital
            for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }}
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary dictionary:

        """)
    +
    layout_comment(str(
        {
            country: capital
            for country, capital
            in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            if country == 'NZ'
        }
        ))
)

SET_COMPREHENSION_COMMENT = (
    layout_comment("""\
        ##### Example Set Comprehension
        """)
    +
    layout_comment(f"""\
        pets = {{
            pet for _person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }}
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout_comment(str(
        {
            pet for _person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
        }
        ))
    +
    layout_comment("""\

        It is also possible to add a simple filter using `if`

        """)
    +
    layout_comment(f"""\
        pets = {{
            pet for person, pet
            in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            if person != 'Elliot'
        }}
        """, is_code=True)
    +
    layout_comment("""\

        produces an ordinary set (i.e. unique members only):

        """)
    +
    layout_comment(str(
        {
            pet for person, pet
                in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                if person != 'Elliot'
        }
        ))
)