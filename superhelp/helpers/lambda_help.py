from .. import conf
from ..gen_utils import layout_comment as layout
from ..helpers import snippet_str_help

@snippet_str_help()
def lambda_advice(snippet, *, repeat=False, **_kwargs):
    """
    Look for use of lambda and give general advice on when / how to use.
    """
    if not 'lambda' in snippet:
        return None
    if repeat:
        return None

    title = layout("""\
    ### Using `lambda`
    """)
    brief_msg = layout("""\

    Lambdas are commonly overused so it is worth reading
    <https://treyhunner.com/2018/09/stop-writing-lambda-expressions/>. Having
    said this, lambdas used appropriately in sorting as key are idiomatic and
    readable as a result.
    """)
    main_msg = (
        layout("""\

        Lambda functions are anonymous functions. They have no name or
        documentation so should only be used where their brevity pros outweigh
        their readability cons.

        In their favour, lambdas are idiomatic when used as the key in sorting
        operations. They are also commonly relied upon when using libraries like
        Pandas (albeit not always wisely).

        Sometimes the alternatives are arguably worse. Consider the following
        alternatives - in this case it may be difficult to improve on the
        lambda:

        #### Use `lambda`

        Using a lambda creates one idiomatic line which obviously sorts by the
        country and city keys in that order
        """)
        +
        layout("""\
        addresses.sort(key=lambda address: (address['country'], address['city']))
        """, is_code=True)
        +
        layout("""\

        #### Alternative 1) use `operator` module

        Using `itemgetter` requires an extra import and it's not as idiomatic.
        Using `operator` functions may become more idiomatic but probably not.
        """)
        +
        layout("""\
        from operator import itemgetter

        addresses.sort(key=(itemgetter('country'), itemgetter('city')))
        """, is_code=True)
        +
        layout("""\

        #### Alternative 2) define a conventional function

        Defining a named function adds many more lines of code and may break up
        the flow of overall program logic. Often not worth it when a very simple
        function.
        """)
        +
        layout("""\
        def country_city(address):
            return (address['country'], address['city'])

        addresses.sort(key=country_city)
        """, is_code=True)
        +
        layout("""\

        Lambdas are a clear mistake when they add nothing or when they become
        too complex.

        Lambdas add nothing apart from confusion and noise when they merely
        apply a function. In the following examples both lines in each pair
        achieve the same result:
        """)
        +
        layout("""\
        words.sort(key=lambda word: len(word))
        words.sort(key=len)

        numbers.sort(key=lambda num: abs(num))
        numbers.sort(key=abs)
        """, is_code=True)
        +
        layout("""\

        In the following example a simple, clearly documented (and testable)
        function is a much better option than a lambda. Compare:
        """)
        +
        layout("""\
        water_iot_vals.sort(
            key=lambda x: min((sum(x) + min(x)) / max(x), 1) + min(x) ** 2)
        """, is_code=True)
        +
        layout("""\
        against the more readable, maintainable, and testable:
        """)
        +
        layout('''\
        def water_quality(vals):
            """
            Reading rank is based on ... etc etc

            The Tajik adjustment was favoured over the more traditional Core
            Value adjustment because ...

            See https://...calculating-clark-coefficients

            :param list vals: ...
            :return: water quality rating
            :rtype: float
            """
            raw_clark_coeff = min((sum(vals) + min(vals)) / max(vals)
            corrected_clark_coeff = min(raw_clark_coeff, 1)
            tajik_adjustment = min(vals) ** 2
            adjusted_clark_coeff = corrected_clark_coeff + tajik_adjustment
            return adjusted_clark_coeff

        water_iot_vals.sort(key=water_quality)
        ''', is_code=True)
        + layout("""\

        The main rule with lambdas is to avoid them unless they make the code
        more readable. And if you must use them, remember that you can still use
        names that convey some meaning - for example `s` for string, `t` for
        tuple, `d` for dict, `l` for list, `nt` for namedtuple, `row` for a row
        etc. They will make the logic more intelligible and make mistakes more
        obvious. For example, x[-1] might be what was intended but it would be
        easier to tell if we saw:

        `lambda l: l[-1]`  ## obviously the last item of a list

        or `lambda s: s[-1]`  ## obviously the last character of a string

        or `lambda d: d[-1]`  ## probably a mistake unless -1 is a key

        Of course, longer names should be used if they help.
        """)
    )
    extra = layout("""\

    Trey Hunner's "Overusing lambda expressions in Python"
    <https://treyhunner.com/2018/09/stop-writing-lambda-expressions/> is well
    worth reading. The position taken in SuperHELP differs in some regards but
    has been influenced by Trey's thinking.

    If using functions from the `operator` module (`itemgetter`, `attrgetter`,
    and `methodcaller`) becomes more common and idiomatic then it could be time
    to substantially reduce the usage of `lambda`.
    """)

    message = {
        conf.BRIEF: title + brief_msg,
        conf.MAIN: title + main_msg,
        conf.EXTRA: extra,
    }
    return message
    