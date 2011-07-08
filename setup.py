from setuptools import setup

REQUIREMENTS = [
    'django',
]

setup(
    name="new_app",
    version='0.0.1',
    author="Author Name",
    author_email="author_email",
    description="Description for new_app.",
    long_description=open('README.txt', 'r').read(),
    url="http://www.example.com",
    packages=("new_app",),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS,
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
