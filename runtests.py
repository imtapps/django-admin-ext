#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'

from django.conf import settings

if not settings.configured:
    #load django settings from example project for tests
    from example import settings as example_settings
    settings.configure(**example_settings.__dict__)

#This import must come after settings config
from django.test.simple import run_tests

def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['sample']

    failures = run_tests(test_args, verbosity=kwargs.get('verbosity', 2), interactive=kwargs.get('interactive', False), failfast=kwargs.get('failfast'))
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)
