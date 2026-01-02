from setuptools import setup, find_packages

setup(
    name="politechie_core",
    version="0.1.3",
    author="Palistha Deshar",
    author_email="palisthadeshar@gmail.com",
    description="A validation library for phone numbers, email addresses, and dates of birth.",
    url="https://github.com/politechielabs/politechie-core.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license_files=["LICENSE"], 
)
