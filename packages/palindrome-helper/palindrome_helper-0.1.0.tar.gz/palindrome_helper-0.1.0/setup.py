from setuptools import setup, find_packages

setup(
    name="palindrome_helper",            # Replace with your package name
    version="0.1.0",                     # Initial version
    author="vishva R",                  # Your name
    author_email="vishvaiioe@gmail.com",  # Your email
    description="A helper file is simple up your palindrome check",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),            # Automatically find packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],             # Minimum Python version
)
