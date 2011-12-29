default: all

all: test flakes pep8 benchmark
	# All good!

envs:
	rm -fr env_*
	virtualenv --no-site-packages -p python2.7 env_27
	virtualenv --no-site-packages -p python3.2 env_32
	virtualenv --no-site-packages -p pypy env_pypy
	
	mkdir -p .download_cache
	for e in env_27 env_32 env_pypy; \
	do \
		$$e/bin/pip install --download-cache=.download_cache Twisted codespeed-client coverage pyflakes pep8; \
	done

test:
	python -m unittest discover -v

test_all:
	for e in env_27 env_32 env_pypy; \
	do \
		$$e/bin/python -m unittest discover -v; \
	done

coverage:
	rm -rf coverage_html .coverage
	mkdir coverage_html
	
	coverage run --source=benchmarking -m unittest discover -v
	coverage html --omit='*/test/*.py' -d coverage_html
	coverage report -m --omit='*/test/*.py'

flakes:
	-pyflakes benchmarking examples

pep8:
	-pep8 --ignore=E501,E241 --repeat --statistics benchmarking examples

benchmark:
	python -m benchmarking --reporter=_test --reporter=Text --reporter=Csv --reporter=Value --reporter=CodeSpeed --revision=test examples.benchmark
