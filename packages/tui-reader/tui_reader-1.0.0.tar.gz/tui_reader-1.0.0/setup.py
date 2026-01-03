from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tui-reader",
    version="1.0.0",
    author="AlAoTach",
    author_email="alaotach@gmail.com",
    description="A terminal-based reader for TXT, MD, and PDF files with themes and voice control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alaotach/tui-reader",
    py_modules=["main"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Editors",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.40.0",
        "pdfminer.six>=20221105",
    ],
    extras_require={
        "voice": [
            "vosk>=0.3.45",
            "pyaudio>=0.2.13",
        ],
    },
    entry_points={
        "console_scripts": [
            "tui-reader=main:main",
        ],
    },
)
