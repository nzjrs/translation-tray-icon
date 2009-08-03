#!/usr/bin/env python

from distutils.core import setup

setup(
    name="translation-tray-icon",
    version="0.1",
    description="PyGtk+ Translation Helper - Translates Selected text",
    author="John Stowers",
    author_email="john.stowers@gmail.com",
    url="http://www.github.com/~nzjrs",
    license="GPL v2",
    scripts=["translation-tray-icon.py"],
    py_modules=["libtranstray"],
    data_files=[
        ('share/applications', ['translation-tray-icon.desktop']),
        ('share/pixmaps', ['translation-tray-icon.svg'])],
)



