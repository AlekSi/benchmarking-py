default: all

all: test flakes pep8
	# All good!

test:
	python -m unittest discover -v
	python -m benchmarking examples.benchmark.benchmark_fibonacci

flakes:
	pyflakes benchmarking examples

pep8:
	pep8 --ignore=E501,E241 --repeat --statistics benchmarking examples
