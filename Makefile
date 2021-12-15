.PHONY: clean-pyc clean-build clean-test docs clean test docker-build docker-test lint help

help:
	@echo "clean - remove all build, test, coverage and python3 artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove python3 file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default python3"
	@echo "docker-build - build a Docker container with the library"
	@echo "docker-test - run unit tests in built Docker container"
	@echo "test-all - run tests on everything"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active python3's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr htmlcov/
	rm -rf .pytest_cache

lint:
	flake8 pypgn

test:
	python3 -m pytest -v --maxfail=2

test-all:
	test

docker-build:
	docker build -t pypgn .

docker-test:
	docker run -it --rm pypgn

release: clean
	python3 setup.py sdist upload
	python3 setup.py bdist_wheel upload

dist: clean
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean
	python3 setup.py install
