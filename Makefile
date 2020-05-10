
git:
	/home/g/projects/superhelp/superhelp/env/bin/nosetests
	sed -i 's/^test_misc()/# test_misc()/' /home/g/projects/superhelp/tests/*.py
	sed -i 's/RECORD_AST = t/RECORD_AST = f/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DEV_MODE = t/DEV_MODE = f/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DO_HTML = f/DO_HTML = t/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DISPLAYER = c/DISPLAYER = h/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DISPLAYER = m/DISPLAYER = h/' /home/g/projects/superhelp/superhelp/conf.py
	git status

upload:

	rm -f dist/*
	/home/g/projects/superhelp/superhelp/env/bin/python3 setup.py sdist bdist_wheel
	/home/g/projects/superhelp/superhelp/env/bin/python3 -m twine upload dist/*
