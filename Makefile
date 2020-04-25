
## Packaging

upload-package:

	sed -i 's/RECORD_AST = t/RECORD_AST = f/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DEV_MODE = t/DEV_MODE = f/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DO_TEST = f/DO_TEST = t/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DO_HTML = f/DO_HTML = t/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/DO_DISPLAYER = f/DO_DISPLAYER = t/' /home/g/projects/superhelp/superhelp/conf.py
	rm -f dist/*
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
