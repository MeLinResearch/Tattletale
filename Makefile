PYTHON ?= python

.PHONY: setup test demo

setup:
	$(PYTHON) -m pip install --no-cache-dir "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
	$(PYTHON) -m pip install --upgrade "certifi>=2026.10.19"
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests

demo:
	$(PYTHON) demo/demo.py
