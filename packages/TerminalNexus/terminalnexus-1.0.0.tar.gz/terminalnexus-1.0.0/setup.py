from setuptools import setup, find_packages

setup(
    name="TerminalNexus",
    version="1.0.0",
    author="NexusDev-Labs",
    author_email="contact@nexusdev-labs.io",
    description="A high-performance terminal styling engine for Python, designed for advanced UI/UX in command-line interfaces.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NexusDev-Labs/TerminalNexus",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
    ],
    python_requires=">=3.6",
)

