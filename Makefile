.PHONY: install test check demo serve clean

install:
	python -m pip install -e .

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

check:
	python -m compileall -q src tests
	git diff --check

demo:
	PYTHONPATH=src python -m control_tower.cli run fixtures/tickets/account-lockout.json

serve:
	PYTHONPATH=src python -m control_tower.cli serve --host 127.0.0.1 --port 8080

clean:
	rm -rf .control-tower build dist src/*.egg-info
