#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = open("requirements.txt").read().strip().split("\n")
dev_requires = open("dev-requirements.txt").read().strip().split("\n")

setup(
    name="python-query-ast",
    version='0.1.0',
    install_requires=install_requires,
    python_requires=">=3.6",
    description="Graph MDM python query output",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Daniel Gazit",
    author_email="danieligazit@gmail.com",
    package_dir={"":"src"},
    packages=find_packages()

)