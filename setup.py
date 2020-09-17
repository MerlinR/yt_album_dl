#!/usr/bin/python
import setuptools
import os


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setuptools.setup(
    name='yt_album_dl',
    version='1.8',
    description='Simple tool to quickly download music videos from Youtube, while splitting albums and correctly applying metadata.',
    author='Merlin Roe',
    author_email='Merlin.Roe@hotmail.co.uk',
    scripts=['yt_album_dl/yt_album_dl', "yt_album_dl/vid_control.py", "yt_album_dl/video_dl.py"],
    license=license,
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/MerlinR/yt_album_dl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
