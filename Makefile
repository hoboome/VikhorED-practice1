PY = python3
SRC = src

.PHONY: run test

run:
	PYTHONPATH=$(SRC) $(PY) -m vshell

test:
	PYTHONPATH=$(SRC) $(PY) -m unittest discover -s tests -p "test_*.py"
