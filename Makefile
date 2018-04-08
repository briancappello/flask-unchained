clean:
	rm -fr build
	rm -fr dist

sdist: clean
	python setup.py sdist

wheel: clean
	python setup.py bdist_wheel

dist: sdist wheel
	twine upload dist/*

.PHONY: clean dist sdist wheel
