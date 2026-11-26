PYTHON ?= python3

.PHONY: test check

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) tools/check_style.py src tests tools
