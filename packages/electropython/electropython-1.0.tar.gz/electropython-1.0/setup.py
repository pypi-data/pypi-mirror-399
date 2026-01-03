from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

setup(
    name="electropython",
    version="1.0",
    author="BlueJFlamesLab",
    description="A utility Python library",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.0",
    licence = "MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
