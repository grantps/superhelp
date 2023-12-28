
.PHONY: git_local
git_local:
	sed -i 's/^test_/# test_/' /home/g/projects/superhelp/tests/*.py  ## deactivate direct running of tests
	sed -i 's/LOG_LEVEL = logging.DEBUG/LOG_LEVEL = logging.INFO/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/RECORD_AST = t/RECORD_AST = f/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/SHOW_OUTPUT = f/SHOW_OUTPUT = t/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/OUTPUT = c/OUTPUT = h/' /home/g/projects/superhelp/superhelp/conf.py
	sed -i 's/OUTPUT = m/OUTPUT = h/' /home/g/projects/superhelp/superhelp/conf.py
	git status
	grep "__version__ = '" /home/g/projects/superhelp/setup.py
	@echo "It's up to you to update and commit"

.PHONY: github
github:
	git push   

.PHONY: upload_pypi
upload_pypi:
	rm -f dist/*
	/home/g/projects/superhelp/env/bin/python3 setup.py sdist bdist_wheel
	/home/g/projects/superhelp/env/bin/python3 -m twine upload dist/*
