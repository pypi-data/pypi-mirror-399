"""
Setup script for godaddycheck.
"""

from setuptools import setup, find_packages

setup(
    name="godaddycheck",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
    ],
    entry_points={
        "console_scripts": [
            "godaddycheck=godaddycheck.cli:main",
        ],
    },
)
