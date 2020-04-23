from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.advisors.enumerate_advisors.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'manual_incrementing': 0,
            }
        ),
        (
            dedent("""\
            n = 1
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            """),
            {
                ROOT + 'manual_incrementing': 1,
            }
        ),
        (
            dedent("""\
            for i in range(2):
                n = 1
                for image in images:
                    if n % 10 == 0:
                        print(f"Just processed image {{n}}")
                    process_image(image)
                    n += 1
            """),
            {
                ROOT + 'manual_incrementing': 1,
            }
        ),
        (
            dedent("""\
            n = 10
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            """),
            {
                ROOT + 'manual_incrementing': 0,  ## not starting at 0, -1, or 1
            }
        ),
        (
            dedent("""\
            n = -1
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            """),
            {
                ROOT + 'manual_incrementing': 1,
            }
        ),
        (
            dedent("""\
            n = -1
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            n = -1
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            """),
            {
                ROOT + 'manual_incrementing': 1,  ## snippet level so just once
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
