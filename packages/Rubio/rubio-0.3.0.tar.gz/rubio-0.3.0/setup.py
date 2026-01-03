from setuptools import setup, find_packages

setup(
    name="Rubio",
    version="0.3.0",
    author="Rubio Team",
    description="The elite Rubika Bot Framework. Fast, Async, and Powerful. @RubioLib",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://t.me/RubioLib",
    packages=find_packages(),
    install_requires=["httpx"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
