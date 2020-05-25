from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.str_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            num = 1
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'assigned_str_overview': 1,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = 'jelly' + 'fish'
            """),
            {
                ROOT + 'assigned_str_overview': 0,  ## only want to cover string combination / interpolation
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 1,
            }
        ),
        (
            dedent("""\
            pet = 'jelly' + 'cat' + 'fish'
            """),
            {
                ROOT + 'assigned_str_overview': 0,  ## only want to cover string combination / interpolation
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 1,
            }
        ),
        (
            dedent("""\
            pet = '%s%s' % ('jelly', 'fish')
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 1,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '%(a)s%(b)s' % {'a': 'jelly', 'b': 'fish'}
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 1,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '{}{}'.format('jelly', 'fish')
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 1,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            pet = '{a}{b}'.format(a='jelly', b='fish')
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 1,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            a = 'jelly'
            b = 'fish'
            pet = f'{a}{b}'
            """),
            {
                ROOT + 'assigned_str_overview': 2,
                ROOT + 'f_str_interpolation': 1,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'cat'
            """),
            {
                ROOT + 'assigned_str_overview': 1,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = 'jelly' + 'fish'
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = '%(a)s%(b)s' % {'a': 'jelly', 'b': 'fish'}
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 1,
                ROOT + 'string_addition': 0,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                pet = '{a}{b}'.format(a='jelly', b='fish')
            """),
            {
                ROOT + 'assigned_str_overview': 0,
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 1,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
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
                ROOT + 'assigned_str_overview': 1,
                ROOT + 'f_str_interpolation': 1,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
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
                ROOT + 'assigned_str_overview': 1,
                ROOT + 'f_str_interpolation': 1,
                ROOT + 'format_str_interpolation': 1,
                ROOT + 'sprintf': 1,
                ROOT + 'string_addition': 1,
            }
        ),
        (
            dedent("""\
            def nameToInitials(name):
                nameList = name.split(' ')
                return "{}.{}".format(nameList[0][0],nameList[1][0])
            """),
            {
                ROOT + 'assigned_str_overview': 0,  ## no overview because not an assigned string
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 1,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,
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
                ROOT + 'assigned_str_overview': 1,  ## no overview because not an assigned string
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,  ## not interested in pushing people towards f-strings in such cases
            }
        ),
        (
            dedent("""\
            class Family:
                pass
            Family.pet = 'cat'
            """),
            {
                ROOT + 'assigned_str_overview': 1,  ## no overview because not an assigned string
                ROOT + 'f_str_interpolation': 0,
                ROOT + 'format_str_interpolation': 0,
                ROOT + 'sprintf': 0,
                ROOT + 'string_addition': 0,  ## not interested in pushing people towards f-strings in such cases
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
