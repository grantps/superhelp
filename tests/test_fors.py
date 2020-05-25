from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.for_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            name_lengths = []
            """),
            {
                ROOT + 'comprehension_option': 0,
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 0,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            name_lengths = []
            for name in ['Noor', 'Grant', ]:
                name_lengths.append(len(name))
            """),
            {
                ROOT + 'comprehension_option': 1,
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 0,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            for pet in ['cat', 'dog']:
                name_lengths = []
                for name in ['Noor', 'Grant', ]:
                    name_lengths.append(len(name))
            """),
            {
                ROOT + 'comprehension_option': 1,  ## the inner one not too long to get advice on a possible list comprehension etc
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 1,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            for pet in ['cat', 'dog']:
                name_lengths = []
                for name in ['Noor', 'Grant', ]:  ## <=========== short
                    name_lengths.append(len(name))
            for name in ['Noor', 'Grant', ]:  ## <=========== short
                name_lengths.append(len(name))
            for name in ['Noor', 'Grant', ]:
                pass
                pass
                name_lengths.append(len(name))
            for name in ['Noor', 'Grant', ]:  ## <=========== short
                name_lengths.append(len(name))
            """),
            {
                ROOT + 'comprehension_option': 3,  ## three of four are not too long to get advice on a possible list comprehension etc
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 1,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            pets = ['cat', 'dog']
            for i in range(len(pets)):
                print(f"My {pets[i]}")
            """),
            {
                ROOT + 'comprehension_option': 1,
                ROOT + 'for_index_iteration': 1,
                ROOT + 'nested_fors': 0,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            for x in range(2):
                pets = ['cat', 'dog']
                for i in range(len(pets)):
                    comment = f"My {pets[i]}"
            """),
            {
                ROOT + 'comprehension_option': 1,  ## one block
                ROOT + 'for_index_iteration': 1,
                ROOT + 'nested_fors': 1,
                ROOT + 'for_else': 0,
            }
        ),
        (
            dedent("""\
            ## https://www.mnn.com/earth-matters/animals/stories/21-animals-with-completely-ridiculous-names
            words = ['Spiny lumpsucker', 'Wunderpus photogenicus', 'Pleasing fungus beetle']
            for word in words:
                if len(word) > 16:
                    break
            else:
                print("Never found any long words")
            """),
            {
                ROOT + 'comprehension_option': 0,  ## one block
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 0,
                ROOT + 'for_else': 1,
            }
        ),
        (
            dedent("""\
            ## https://www.mnn.com/earth-matters/animals/stories/21-animals-with-completely-ridiculous-names
            words = ['Spiny lumpsucker', 'Wunderpus photogenicus', 'Pleasing fungus beetle']
            for i in range(2):
                for word in words:
                    if len(word) > 16:
                        break
                else:
                    print("Never found any long words")
            """),
            {
                ROOT + 'comprehension_option': 0,  ## one block
                ROOT + 'for_index_iteration': 0,
                ROOT + 'nested_fors': 1,
                ROOT + 'for_else': 1,
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
