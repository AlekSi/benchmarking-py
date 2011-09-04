default: all

all: test flakes pep8 benchmark
	# All good!

test:
	python -m unittest discover -v

flakes:
	pyflakes benchmarking examples

pep8:
	pep8 --ignore=E501,E241 --repeat --statistics benchmarking examples

benchmark:
	python -m benchmarking --reporter=_test --reporter=Text --reporter=Csv --reporter=Value examples.benchmark.benchmark_fibonacci
