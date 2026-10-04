PY = python3
SRC = src

.PHONY: run test fixtures demo check

run:
	PYTHONPATH=$(SRC) $(PY) -m vshell

test:
	PYTHONPATH=$(SRC) $(PY) -m unittest discover -s tests -p "test_*.py"

fixtures:
	$(PY) fixtures/build_fixtures.py

demo: fixtures
	PYTHONPATH=$(SRC) $(PY) -m vshell -v fixtures/out/deep.zip \
		-s examples/stage4.vsh

check: fixtures
	./os_scripts/check_args.sh --console
	./os_scripts/check_vfs.sh --console
