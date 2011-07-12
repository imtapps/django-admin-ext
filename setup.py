from setuptools import setup

REQUIREMENTS = [
    'django',
]

TEST_REQUIREMENTS = [
    'selenium>=2.0'
] + REQUIREMENTS

setup(
    name="django-admin-ext",
    version='0.1.1',
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
)
