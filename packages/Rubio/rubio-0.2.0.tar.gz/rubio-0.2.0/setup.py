from setuptools import setup, find_packages

setup(
    name="Rubio",
    version="0.2.0",
    author="Rubio Team",
    description="The most powerful and fast Python wrapper for Rubika Bot API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://rubika.ir/RubioLib",
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
