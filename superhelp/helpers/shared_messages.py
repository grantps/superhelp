from superhelp.conf import Level
from superhelp.gen_utils import layout_comment as layout

def get_aop_msg():
    return layout("""

        Some aspects of code apply to lots of different parts of the code base
        e.g. logging, or security. These can be thought of as "cross-cutting
        concerns" from an Aspect-Oriented Programming point of view. The problem
        is that a lot of code gets repeated e.g. if every function has to
        implement its own logging or has to handle its own security. Even if
        there is some shared functionality it can often require special wiring
        into other code. In short, coping with cross-cutting concerns can be
        painful.

        Decorators and Context Managers are ways Python provides of
        concentrating cross-cutting concerns into single pieces of code in an
        elegant way. They DRY out your code (see
        <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>). And because
        they are very widely used, it is worth learning how to use them, even if
        you don't take the step of writing your own.

    """)

def get_unpacking_msg():
    return (
        layout("""\
            Unpacking is much more pythonic than using indexes to pull a
            sequence apart into names (variables). For example:

            """)
        +
        layout("""\

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
            ignore or even mop up multiple unused values into a single value
            using an asterisk.

            For example:

            """)
        +
        layout("""\
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
        layout("""\

            or:

            """)
        +
        layout("""\
            lat, lon, *unused = location
            """, is_code=True)
        +
        layout(f"""\

            Note - unused, in this case, would be ['Auckland', 'Mt Albert']

            """)
        )

def get_general_comprehension_msg():
    return layout("""\
        Comprehensions are one the great things about Python. To see why, have a
        look at Raymond Hettinger's classic talk "Transforming Code into
        Beautiful, Idiomatic Python" <https://youtu.be/OSGv2VnC0go?t=2738> where
        he explains the rationale. In short, if the goal of your code can be
        expressed as a single English sentence then it might belong on one line.
        The code should say what it is doing more than how it is doing it.
        Comprehensions are declarative and that is A Very Good Thing™.

        Pro tip: don't make comprehensions *in*comprehensions ;-). If your
        comprehension is hard to read it is probably better rewritten as a
        looping structure.
        """)

def get_list_comprehension_msg():
    """
    Not used it seems
    """
    return (
        layout("""\

            #### Example List Comprehension:

            """)
        +
        layout("""\
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
        layout('`' + str(
            {
                len(name)
                for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
            }
            ) + '`')
        +
        layout("""\

            It is also possible to add a simple filter using `if`

            """)
        +
        layout("""\
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
        layout('`' + str(
            {
                len(name)
                for name in ['Tinky Winky', 'Dipsy', 'La La', 'Po']
                if not name.startswith('T')
            }
            ) + '`')
    )

def get_dict_comprehension_msg():
    return (
        layout("""\

        #### Example Dictionary Comprehension:

        """)
        +
        layout("""\
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
        layout('`' + str(
            {
                country: capital
                for country, capital
                in [('NZ', 'Wellington'), ('Italy', 'Rome')]
            }
            ) + '`')
        +
        layout("""\

            It is also possible to add a simple filter using `if`

            """)
        +
        layout("""\
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
        layout('`' + str(
            {
                country: capital
                for country, capital
                in [('NZ', 'Wellington'), ('Italy', 'Rome')]
                if country == 'NZ'
            }
            ) + '`')
    )

def get_set_comprehension_msg():
    return (
        layout("""\

            #### Example Set Comprehension

            """)
        +
        layout("""\
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
        layout('`' + str(
            {
                pet for _person, pet
                    in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
            }
            ) + '`')
        +
        layout("""\

            It is also possible to add a simple filter using `if`

            """)
        +
        layout("""\
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
        layout('`' + str(
            {
                pet for person, pet
                    in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                    if person != 'Elliot'
            }
            ) + '`')
    )

def get_dataclass_msg(level: Level, *, in_named_tuple_context=False):
    validation_msg = (layout("""\
        Validation is also easy to add to dataclasses e.g.
        """)
        +
        layout("""\
        @dataclass
        class People:
             name: str
             IQ: int = 100

             def __post_init__(self):
                 if not 70 <= self.IQ <= 170:
                     raise ValueError(f"Invalid IQ ({self.IQ})")
        """, is_code=True))
    derived_values_msg = (
        layout("""\
            It is also easy to add derived values e.g.
            """)
        +
        layout("""\
            @dataclass
            class Rect:
                 length: float
                 width: float

                 def __post_init __(self):
                     self.area = self.length * self.width
            """, is_code=True)
    )
    if in_named_tuple_context:
        simple_msg = (
            layout("""\
    
            Dataclasses make it much easier to display default values e.g.
            """)
            +
            layout("""\
            @dataclass
            class People:
                 name: str
                 IQ: int = 100
            """, is_code=True)
            +
            validation_msg
            +
            derived_values_msg
        )
    else:
        simple_msg = (
            layout("""\

            Dataclasses make it easy to display type hints and default values e.g.
            """)
            +
            layout("""\
                @dataclass
                class People:
                     name: str
                     IQ: int = 100
                """, is_code=True)
            +
            validation_msg
            +
            derived_values_msg
        )
    if level == Level.BRIEF:
        msg = simple_msg
    elif level == Level.MAIN:
        msg = simple_msg + main_msg
    elif level == Level.EXTRA:
        msg = extra_msg
    return msg
