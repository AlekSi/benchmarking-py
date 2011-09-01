from __future__ import division, print_function, absolute_import

import sys
from optparse import OptionParser

import benchmarking
import benchmarking.reporters

all_reporters = benchmarking.reporters.ReporterFactory.all_reporters()

parser = OptionParser()
parser.add_option("--reporter", help="Reporter to use, may be given several times. Available reporters: %s" % ', '.join(all_reporters),
                  type="choice", choices=all_reporters)
options, args = parser.parse_args()

modules = sys.argv[1:]
for module in modules:
    print("importing %s" % (module,), file=sys.stderr)
    __import__(module)

reporters = [options.reporter]
reporter = benchmarking.reporters.MultiReporter(reporters=options)
benchmarking.main()
sys.exit(0)
