import re
import os

from distutils.core import Command, setup

from djadmin_ext import VERSION

REQUIREMENTS = [
    'django',
]

TEST_REQUIREMENTS = [
    'selenium>=2.0',
    'django-jenkins',
    'pep8',
    'pyflakes',
]

def do_setup():
    setup(
        name="django-admin-ext",
        version=VERSION,
        author="Aaron Madison and Matthew J Morrison",
        description="Extensions to Django's admin site to add an ajax view.",
        long_description=open('README.txt', 'r').read(),
        url="https://github.com/imtapps/django-admin-ext",
        packages=("djadmin_ext",),
        include_package_data=True,
        install_requires=REQUIREMENTS,
        tests_require=TEST_REQUIREMENTS,
        test_suite='runtests.runtests',
        zip_safe=False,
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
        cmdclass={
            'install_dev': InstallDependencies,
            'uninstall_dev': UninstallDependencies,
        },
    )

class PipDependencies(Command):
    pip_command = ""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_all_dependencies(self):
        """
        replace all > or < in the dependencies so the system does not
        try to redirect stdin or stdout from/to a file.
        """
        command_line_deps = ' '.join(REQUIREMENTS + TEST_REQUIREMENTS)
        return re.sub(re.compile(r'([<>])'), r'\\\1', command_line_deps)

    def run(self):
        os.system("pip %s %s" % (self.pip_command, self.get_all_dependencies()))

class InstallDependencies(PipDependencies):
    pip_command = 'install'

class UninstallDependencies(PipDependencies):
    pip_command = 'uninstall'

if __name__ == '__main__':
    do_setup()