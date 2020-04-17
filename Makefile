
## Packaging

upload-package:

	rm -f dist/*
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
