from textwrap import dedent

from tests import check_as_expected

ROOT = 'superhelp.helpers.decorator_help.'

def test_misc():
    test_conf = [
        (
            dedent("""\
            pet = 'cat'
            """),
            {
                ROOT + 'decorator_overview': 0,
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
                ROOT + 'decorator_overview': 2,  ## includes wraps
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
                ROOT + 'decorator_overview': 3,  ## each block should get the message
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

            @app.route('/sheet_already_exists')
            def sheet_already_exists() -> Tuple[Dict[str, bool], int]:
                '''Returns a boolean for whether or not a sheet with the requested
                name exists.
                :return: Whether or not it exists.
                :rtype: Tuple[Dict[str, bool], int]
                '''
                # Finds the name of the sheet to be found.
                name = request.args['name']
                # Finds the name of a sheet to be ignored even if it exists.
                prior = request.args.get('prior', None)
                # If the name is the same as the one ignored, returns False.
                if name == prior:
                    return {'already_there': False}, 200
                # Establishes a connection.
                conn = get_connection()
                # Finds out whether the sheet exists or not.
                already_there = bool(conn.execute(
                    '''
                    SELECT 1 FROM sheets
                    INNER JOIN translators
                        ON translators.translator = sheets.translator
                    WHERE last_used = (
                        SELECT MAX(last_used) FROM translators
                    )
                    AND name = ?
                    LIMIT 1
                    ''', (request.args['name'],)
                ).fetchall())
                # Returns the result.
                return {'already_there': already_there}, 200
            """),
            {
                ROOT + 'decorator_overview': 4,  ## each block should get the message
            }
        ),
        (
            dedent("""\
            from dataclasses import dataclass
            
            @dataclass
            class Sausage:
                pass
            """),
            {
                ROOT + 'decorator_overview': 0,  ## decorator for a dataclass should be ignored (and handled under dataclasses)
            }
        ),
    ]
    check_as_expected(test_conf, execute_code=True)
    check_as_expected(test_conf, execute_code=False)

# test_misc()
