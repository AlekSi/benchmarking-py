from __future__ import division, print_function, absolute_import

import sys
from optparse import OptionParser, OptionGroup

import benchmarking
from benchmarking.reporters import ReporterFactory, MultiReporter

all_reporters = ReporterFactory.all_reporters()

parser = OptionParser(usage='%prog [options] [benchmark modules]')
parser.add_option("--reporter", help="Reporter to use, may be given several times. Available reporters: %s" % ', '.join(all_reporters),
                  action="append", type="choice", choices=all_reporters + ['_test'])
parser.add_option('--more-is-better', help='Report speed, not time per call.', action='store_true', default=False)
parser.add_option('--revision', help='SCM revision number or commit ID', metavar='ID')
parser.add_option('--branch', help='SCM branch')

cs_group = OptionGroup(parser, 'CodeSpeed reporter options')
cs_group.add_option('--cs-url', help='CodeSpeed root url (defaults to %default)',
                    metavar='URL', default='http://localhost:8000/')
parser.add_option_group(cs_group)

options, args = parser.parse_args()

if not len(args):
    parser.error('benchmark modules list is empty')

for module in args:
    print("importing %s" % (module,), file=sys.stderr)
    __import__(module)

if options.reporter is None:
    options.reporter = ['Value']

reporters = []
for reporter in options.reporter:
    kwargs = {}
    if reporter == 'CodeSpeed':
        # FIXME those are options of all reporters / runner
        kwargs['root_url'] = options.cs_url
        kwargs['less_is_better'] = not options.more_is_better
        kwargs['commitid'] = options.revision   # TODO environ
        kwargs['branch'] = options.branch
    reporters.append(ReporterFactory.by_name(reporter, **kwargs))

multi_reporter = MultiReporter(reporters=reporters)
benchmarking.main(reporter=multi_reporter)
sys.exit(0)
