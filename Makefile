sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

dist: sdist wheel
	twine upload dist/*

.PHONY: dist sdist wheel
