from setuptools import setup, find_packages
from pathlib import Path

# Paths
this_directory = Path(__file__).parent

# Read README and CHANGELOG
long_description = ""
for filename in ("README.md", "CHANGELOG.md"):
    file_path = this_directory / filename
    if file_path.exists():
        long_description += file_path.read_text(encoding="utf-8") + "\n\n"

setup(
    name="ELDB",               # Unique package name on PyPI
    version="1.3.1",             # Current version
    packages=find_packages(),  # Single file module
    author="Baraa",
    author_email="cenomi3041@gavrom.com",
    description="A simple ELDB engine for Python",
    long_description=long_description.strip(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Database",
    ],
    python_requires=">=3.6",
    install_requires=[]
)
