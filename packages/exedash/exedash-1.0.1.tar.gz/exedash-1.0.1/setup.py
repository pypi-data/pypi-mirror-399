# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="exedash",
    version="1.0.1",
    author="louati Mahdi",
    author_email="louatimahdi390@gmail.com", 
    description="Turn any Pandas DataFrame into a powerful Excel dashboard with one line of code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mahdi123-tech", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'xlsxwriter',
    ],
)