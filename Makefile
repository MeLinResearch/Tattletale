PYTHON ?= python

.PHONY: setup test demo

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests

demo:
	$(PYTHON) demo/demo.py
