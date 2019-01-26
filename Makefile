init:
	pip install -r requirements.txt

test:
	py.test --verbose tests

.PHONY: init test