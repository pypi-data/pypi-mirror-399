from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="gicom",
    version="0.2.1",
    description="AI-powered Git commit messages generated directly from your terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Amin Torabi",
    url="https://github.com/amintorabi88/gicom",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9",
        "rich>=13",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "pyperclip",
    ],
    entry_points={
        "console_scripts": [
            "gicom=gicom.main:app",
        ],
    },
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
)
