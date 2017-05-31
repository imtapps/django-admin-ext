from setuptools import setup

setup(
    name="django-admin-ext",
    version='2.0.0',
    author="IMTApps",
    description="Extensions to Django's admin site to add an ajax view.",
    long_description=open('README.txt', 'r').read(),
    url="https://github.com/imtapps/django-admin-ext",
    packages=("djadmin_ext",),
    include_package_data=True,
    install_requires=open('requirements/dist.txt', 'r').read().split('\n'),
    zip_safe=False,
    classifiers=[
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