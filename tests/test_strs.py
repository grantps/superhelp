from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            num = 1
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 1,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = 'jelly' + 'fish'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,  ## only want to cover string combination / interpolation
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 1,
            }
        ),
        (
            dedent("""\
            pet = '%s%s' % ('jelly', 'fish')
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 1,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '%(a)s%(b)s' % {'a': 'jelly', 'b': 'fish'}
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 1,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '{}{}'.format('jelly', 'fish')
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 1,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '{a}{b}'.format(a='jelly', b='fish')
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 1,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            a = 'jelly'
            b = 'fish'
            pet = f'{a}{b}'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 2,
                'superhelp.advisors.str_advisors.f_str_interpolation': 1,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'cat'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 1,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'jelly' + 'fish'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = '%(a)s%(b)s' % {'a': 'jelly', 'b': 'fish'}
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 1,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = '{a}{b}'.format(a='jelly', b='fish')
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 1,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                a = 'jelly'
                b = 'fish'
                pet = f'{a}{b}'
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 1,
                'superhelp.advisors.str_advisors.f_str_interpolation': 1,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                a = 'jelly'
                b = 'fish'
                pet = f'{a}{b}'
                your_pet = 'cat' + 'fish'
                our_pet = '{a}{b}'.format(a='king', b='fisher')
                their_pet = '%(a)s%(b)s' % {'a': 'sting', 'b': 'ray'}
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 1,
                'superhelp.advisors.str_advisors.f_str_interpolation': 1,
                'superhelp.advisors.str_advisors.format_str_interpolation': 1,
                'superhelp.advisors.str_advisors.sprintf': 1,
                'superhelp.advisors.str_advisors.string_addition': 1,
            }
        ),
        (
            dedent("""\
            def nameToInitials(name):
                nameList = name.split(' ')
                return "{}.{}".format(nameList[0][0],nameList[1][0])
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 0,  ## no overview because not an assigned string
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 1,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,
            }
        ),
        (
            dedent("""\
            def DNAtoRNA(DNAstring):
                newString = ''
                for char in DNAstring:
                    if char!= 'T':
                        newString+= char
                    else:
                        newString+='U'
                return newString
            """),
            {
                'superhelp.advisors.str_advisors.assigned_str_overview': 1,  ## no overview because not an assigned string
                'superhelp.advisors.str_advisors.f_str_interpolation': 0,
                'superhelp.advisors.str_advisors.format_str_interpolation': 0,
                'superhelp.advisors.str_advisors.sprintf': 0,
                'superhelp.advisors.str_advisors.string_addition': 0,  ## not interested in pushing people towards f-strings in such cases
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
