from __future__ import print_function

import sys
modules = sys.argv[1:]
for module in modules:
    print("importing %s" % (module,), file=sys.stderr)
    __import__(module)

import benchmarking
benchmarking.main()
sys.exit(0)
