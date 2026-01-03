from setuptools import setup, find_packages

setup(
    name="Rubio",
    version="0.1.0",
    author="Your Name",
    description="A clean, lightweight Python wrapper for the Rubika Bot API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rubio",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
