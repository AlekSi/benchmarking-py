default: all

all: test flakes pep8 benchmark
	# All good!

envs:
	rm -fr env_*
	#virtualenv --no-site-packages -p python2.6 env_26
	virtualenv --no-site-packages -p python2.7 env_27
	virtualenv --no-site-packages -p python3.2 env_32
	virtualenv --no-site-packages -p pypy env_pypy

test:
	python -m unittest discover -v

flakes:
	-pyflakes benchmarking examples

pep8:
	-pep8 --ignore=E501,E241 --repeat --statistics benchmarking examples

benchmark:
	python -m benchmarking --reporter=_test --reporter=Text --reporter=Csv --reporter=Value --reporter=CodeSpeed --revision=test examples.benchmark.benchmark_fibonacci examples.benchmark.benchmark_deferred
