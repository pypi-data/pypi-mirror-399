from setuptools import setup, find_packages

setup(
    name="pygen_modules",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pygen=pygen_modules.cli:main"]
    },
)
