import os

from setuptools import setup, find_packages
from dockermake.version import VERSION

with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding='UTF-8') as readme:
    long_description = readme.read()

setup(
    name="docker-make",
    version=VERSION,
    description="A helper which can be used to compile Dockerfiles into images.",
    long_description=long_description,

    url="https://github.com/fi-ts/docker-make",
    author="fi-ts",
    license="MIT",

    classifiers=[
        "Development Status :: 5 - Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7"
    ],

    keywords="docker make dockerfile build push lint devops",
    packages=find_packages(exclude=["test"]),
    package_data=dict(dockermake=["config/validators/schemas/*.json", "registries/schemas/*.json"]),
    install_requires=[
        "ConfigArgParse",
        "mock",
        "jsonschema>=2.6.0,<3",
        "PyYAML>=5.3.1,<6",
        "pyparsing==2.3.0",
        "tabulate>=0.8.2,<1",
        "termcolor",
    ],
    extras_require=dict(
        dev=[
            "nose",
            "coverage",
            "testfixtures",
            "setuptools-lint"
        ]
    ),
    data_files=[('bin', ['docker-make'])],
    test_suite="test"
)
