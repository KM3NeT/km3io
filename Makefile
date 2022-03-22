PKGNAME=km3io

default: build

all: install

install: 
	pip install .

install-dev:
	pip install -e ".[dev]"
	python -m ipykernel install --user --name=km3io

clean:
	python setup.py clean --all

test: 
	py.test --junitxml=./reports/junit.xml -o junit_suite_name=$(PKGNAME) tests

test-cov:
	py.test --cov src/km3io --cov-report term-missing --cov-report xml:reports/coverage.xml --cov-report html:reports/coverage tests

test-loop: 
	py.test tests
	ptw --ext=.py,.pyx --ignore=doc tests

flake8: 
	py.test --flake8

pep8: flake8

docstyle: 
	py.test --docstyle

lint: 
	py.test --pylint

.PHONY: black
black:
	black --exclude '/_definitions/|version.py' src/km3io
	black examples
	black tests
	black doc/conf.py
	black setup.py

.PHONY: black-check
black-check:
	black --check --exclude '/_definitions/|version.py' src/km3io
	black --check examples
	black --check tests
	black --check doc/conf.py
	black --check setup.py


.PHONY: all clean install install-dev test  test-nocov flake8 pep8 docstyle black black-check
