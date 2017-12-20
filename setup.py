#!/usr/bin/python

import os
from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='yt_album_dl',
    version='1.0',
    description='Simple tool to quickly download music videos from Youtube, while splitting albums and correctly applying metadata.',
    long_description=readme,
    author='Merlin Roe',
    author_email='merlin.roe@hotmail.co.uk',
    license=license,
    package_dir = {'yt_album_dl'},
    install_requires=['youtube-dl', 'pydub'],
)