from setuptools import setup, find_packages
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="math_tols",
    version="1.1.8",
    packages=find_packages(),
    install_requires=[
    ],
    python_requires='>=3.7',
    description="Ultimate full math tools library",
    long_description=long_description, 
    long_description_content_type="text/markdown", 
    author="Abolfazl",
    author_email="your.email@example.com", 
    url="https://github.com/username/scrt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License", 
    ],
)