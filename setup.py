import os

from setuptools import find_packages, setup


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

setup(
    name="virtue",
    url="https://github.com/Julian/Virtue",

    description="A test runner with virtue",
    long_description=long_description,

    author="Julian Berman",
    author_email="Julian@GrayVines.com",

    packages=find_packages(),
    scripts=[os.path.join(BIN_DIR, bin) for bin in os.listdir(BIN_DIR)],

    setup_requires=["vcversioner>=2.16.0.0"],
    vcversioner={"version_module_paths": ["virtue/_version.py"]},

    install_requires=[
        "attrs>=16.3.0",
        "colorama",
        "pyrsistent",
        "Twisted>=14.0.0",
    ],

    classifiers=classifiers,
    license="MIT",
)
