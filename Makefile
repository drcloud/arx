.PHONY: test check flake8

test:
	tox

check: flake8

flake8:
	flake8 arx setup.py
