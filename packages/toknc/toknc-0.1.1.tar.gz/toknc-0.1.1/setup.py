from setuptools import setup, find_packages

setup(
    name="toknc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "tiktoken": ["tiktoken>=0.5.0"],
    },
    entry_points={
        "console_scripts": [
            "toknc=toknc:main",
        ],
    },
)
