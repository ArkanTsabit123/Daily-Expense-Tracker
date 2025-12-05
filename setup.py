# daily-expense-tracker/setup.py

"""
Setup script for Daily Expense Tracker
"""

import sys

# Try to import setuptools
try:
    from setuptools import find_packages, setup
except ImportError:
    print("Installing setuptools...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    from setuptools import find_packages, setup

def read_requirements():
    """Read requirements from requirements.txt"""
    requirements = []
    # Default requirements if file doesn't exist
    default_requirements = [
        "matplotlib>=3.7.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
    ]
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Clean the line
                line = line.split("#")[0].strip()
                if line and not line.isspace():
                    requirements.append(line)
    except FileNotFoundError:
        print("requirements.txt not found, using defaults")
        requirements = default_requirements
    if not requirements:
        requirements = default_requirements
    return requirements

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get requirements
install_requires = read_requirements()

setup(
    name="daily-expense-tracker",
    version="1.0.0",
    author="Arkan Tsabit",
    author_email="aarkantsabit@gmail.com",
    description="Python application for tracking daily expenses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArkanTsabit123/Daily-Expense-Tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "expense-tracker=main:main",
        ],
    },
    include_package_data=True,
)
