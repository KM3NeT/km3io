PKGNAME=km3io

default: build

all: install

install:
	pip install .

install-dev:
	pip install -e ".[dev]"
	pip install -e ".[extras]"
	python -m ipykernel install --user --name=km3io

venv:
	python3 -m venv venv

test:
	python -m pytest --junitxml=./reports/junit.xml -o junit_suite_name=$(PKGNAME) tests

test-cov:
	python -m pytest --cov src/$(PKGNAME) --cov-report term-missing --cov-report xml:reports/coverage.xml --cov-report html:reports/coverage tests

test-loop:
	python -m pytest tests
	ptw --ext=.py,.pyx --ignore=doc tests

black:
	black src/$(PKGNAME)
	black doc/conf.py
	black tests
	black examples

.PHONY: all clean install install-dev venv test test-cov test-loop black
