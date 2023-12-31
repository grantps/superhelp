"""
https://github.com/grantps/superhelp/wiki
(env) g@g-desktop:~/projects/superhelp$ python3 -m pip install python-dotenv
"""
import logging
import os
from subprocess import run

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

api_token = os.getenv('PYPI_SUPERHELP_API_TOKEN')

logging.info("About to clear dist folder ...")
run('cd /home/g/projects/superhelp/ && rm -f dist/*', shell=True)
logging.info("Cleared dist folder")
logging.info("About to create wheel ...")
run('/home/g/projects/superhelp/env/bin/python3 setup.py sdist bdist_wheel', shell=True)
logging.info("Created wheel")
logging.info("About to push to PyPI ...")
run(f"/home/g/projects/superhelp/env/bin/python3 -m twine upload -u '__token__' -p '{api_token}' dist/*", shell=True)
logging.info("Pushed to PyPI")
logging.info("Finished :-)")
