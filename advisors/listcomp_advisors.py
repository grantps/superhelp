from textwrap import dedent

from advisors import advisor, get_name, get_val, code_indent
import conf

@advisor(conf.LISTCOMP_ELEMENT_TYPE)
def listcomp_overview(element, std_imports, code_str):
    name = get_name(element)
    items = get_val(std_imports, code_str, name)
    message = {
        conf.BRIEF: dedent(f"""
            `{name}` is a list comprehension returning a list
            with {len(items):,} items: {items}
        """),
        conf.EXTRA: (
            dedent(f"""\
            #### Other "comprehensions"

            Comprehensions are one the great things about Python. To see why,
            have a look at Raymond Hettinger's classic talk "Transforming Code
            into Beautiful, Idiomatic Python"
            https://youtu.be/OSGv2VnC0go?t=2738 where he explains the
            rationale. In short, if the goal of your code can be expressed as a
            single English sentence then it might belong on one line. The code
            should say what it is doing more than how it is doing it.
            Comprehensions are declarative and that is good.

            Python also lets you make:

            1) dictionary comprehensions e.g.

            """)
            +
            code_indent(
                dedent(f"""\
                    {conf.MD_PYTHON_CODE_START}
                    country2capital = {{
                        country: capital
                        for country, capital in [('NZ', 'Wellington'), ('Italy', 'Rome')]
                    }}
                    """)
            )
            +
            dedent("\nproduces an ordinary dictionary:\n")
            +
            dedent(str(
                {
                    country: capital
                    for country, capital
                    in [('NZ', 'Wellington'), ('Italy', 'Rome')]
                }
            ))
            +
            dedent(f"""\n\n
            2) set comprehensions e.g.

            """)
            +
            code_indent(
                dedent(f"""\
                    {conf.MD_PYTHON_CODE_START}
                    pets = {{
                        pet for _person, pet
                        in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                    }}
                    """)
            )
            +
            dedent("\nproduces an ordinary set (i.e. unique members only):\n")
            +
            dedent(str(
                {
                    pet for _person, pet
                        in [('Rachel', 'cat'), ('Elliot', 'goat'), ('Giles', 'cat'),]
                }
            ))
            +
            dedent("""\n
            Pro tip: don't make comprehension *in*comprehensions ;-). If it is
            hard to read it is probably better written as a looping structure.
            """)
        ),
    }
    return message
