import site
import sys
from os.path import abspath, dirname
from textwrap import dedent

import clingo
from skbuild import setup

if not site.ENABLE_USER_SITE and "--user" in sys.argv[1:]:
    site.ENABLE_USER_SITE = True

clingopath = abspath(dirname(clingo.__file__))

setup(
    version="1.0.0",
    name="cmapf",
    description="MAPF utilities for clingo written in C++.",
    long_description=dedent(
        """\
        MAPF utilities for clingo written in C++.
        """
    ),
    long_description_content_type="text/markdown",
    author="Roland Kaminski",
    author_email="kaminski@cs.uni-potsdam.de",
    license="MIT",
    url="https://github.com/rkaminsk/cmapf",
    install_requires=["cffi", "clingo"],
    cmake_args=[
        "-DCMAPF_MANAGE_RPATH=OFF",
        "-DPYCMAPF_ENABLE=pip",
        "-DPYCMAPF_INSTALL_DIR=libpycmapf",
        f"-DPYCMAPF_PIP_PATH={clingopath}",
    ],
    packages=["cmapf"],
    package_data={"cmapf": ["py.typed", "import__cmapf.lib", "cmapf.h"]},
    package_dir={"": "libpycmapf"},
    python_requires=">=3.6",
)
