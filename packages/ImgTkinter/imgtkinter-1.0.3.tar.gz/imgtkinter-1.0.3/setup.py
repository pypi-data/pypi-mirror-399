# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ImgTkinter",
    version="1.0.3",
    author="Penr",
    author_email="1944542244@qq.com",
    description="A powerful image classification and management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/peng0928/ImgTkinter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyQt5>=5.15.0",
        "pypinyin>=0.44.0",
    ],
    entry_points={
        "console_scripts": [
            "Primg=ImgTkinter.ImgTkinter:main",
        ],
    },
    include_package_data=True,
    keywords=["image", "classification", "management", "PyQt5", "desktop"],
    project_urls={
        "Bug Reports": "https://github.com/peng0928/ImgTkinter/issues",
        "Source": "https://github.com/peng0928/ImgTkinter",
    },
)