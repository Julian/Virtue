import os

from setuptools import find_packages, setup

from virtue import __version__
from virtue.compat import PY26


BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    long_description = readme.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

install_requires = ["Twisted>=14.0.0"]
if PY26:
    install_requires.extend(["argparse", "unittest2"])

setup(
    name="virtue",
    version=__version__,
    packages=find_packages(),
    scripts=[os.path.join(BIN_DIR, bin) for bin in os.listdir(BIN_DIR)],
    install_requires=install_requires,
    author="Julian Berman",
    author_email="Julian@GrayVines.com",
    classifiers=classifiers,
    description="A test runner with virtue",
    license="MIT",
    long_description=long_description,
    url="https://github.com/Julian/Virtue",
)
