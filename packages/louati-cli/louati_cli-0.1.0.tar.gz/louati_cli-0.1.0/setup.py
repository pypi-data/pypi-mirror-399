from setuptools import setup, find_packages
import re

# Read version from src/louati_cli/__init__.py
version = "0.1.0"
with open("src/louati_cli/__init__.py") as f:
    version_match = re.search(r'^__version__ = ["\']([^"\']*)["\']', f.read(), re.M)
    if version_match:
        version = version_match.group(1)

setup(
    name="louati-cli",
    version=version,
    author="Louati Mahdi",
    author_email="louatimahdi390@gmail.com",
    description="Interactive CLI to explore Louati Mahdi's data engineering expertise",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mahdi123-tech",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'click>=8.1.3',
        'termcolor>=2.3.0',
        'pyfiglet>=0.8.post1',
        'yaspin>=2.2.0',
    ],
    entry_points={
        'console_scripts': [
            'louati-cli=louati_cli.cli:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Terminals",
    ],
    python_requires=">=3.8",
)