from textwrap import dedent

from tests import check_as_expected

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                'superhelp.advisors.decorator_advisors.decorator_overview': 0,
            }
        ),
        (
            dedent("""\
            from functools import wraps
            def tweet(func):
                @wraps(func)
                def wrapper(message):
                    func(message)
                    print(f"I'm tweeting the message {message}")
                return wrapper
            
            @tweet
            def say(message):
                print(message)
            """),
            {
                'superhelp.advisors.decorator_advisors.decorator_overview': 2,  ## includes wraps
            }
        ),
        (
            dedent("""\
            from functools import wraps
            def tweet(func):
                @wraps(func)  ## ignored even though it is a decorator
                def wrapper(message):
                    func(message)
                    print(f"I'm tweeting the message {message}")
                return wrapper
            
            @email
            @tweet
            def say(message):
                print(message)

            say("sausage!!")

            @tweet
            def yell(message):
                print(message.upper())
            """),
            {
                'superhelp.advisors.decorator_advisors.decorator_overview': 3,  ## each block should get the message
            }
        ),
    ]
    check_as_expected(test_conf)

# test_misc()
