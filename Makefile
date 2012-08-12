default: all

all: test style benchmark
	# All good!

envs:
	rm -fr env_*
	virtualenv --distribute --no-site-packages -p python2.6 env_26
	virtualenv --distribute --no-site-packages -p python2.7 env_27
	virtualenv --distribute --no-site-packages -p python3.2 env_32
	virtualenv --distribute --no-site-packages -p pypy env_pypy
	
	mkdir -p .download_cache
	for e in env_26 env_27 env_32 env_pypy; \
	do \
		$$e/bin/pip install --download-cache=.download_cache codespeed-client coverage pep8 Sphinx; \
	done
	for e in env_26 env_27 env_pypy; \
	do \
		$$e/bin/pip install --download-cache=.download_cache pyflakes Twisted unittest2; \
	done

test_all:
	for e in env_26 env_27 env_pypy; \
	do \
		$$e/bin/unit2 discover -v; \
	done
	env_32/bin/python -m unittest discover -v

test:
	python -m unittest discover -v

coverage:
	rm -rf coverage_html .coverage
	mkdir coverage_html
	
	coverage run --source=benchmarking -m unittest discover -v
	coverage html --omit='*/test/*.py' -d coverage_html
	coverage report -m --omit='*/test/*.py'

style: flakes pep8

flakes:
	-pyflakes benchmarking examples

pep8:
	-pep8 --ignore=E501,E241 --repeat --statistics benchmarking examples

benchmark:
	python -m benchmarking --reporter=_test --reporter=Text --reporter=Csv --reporter=Value --reporter=CodeSpeed --revision=test examples.benchmark

docs:
	cd docs && make html

.PHONY: docs
