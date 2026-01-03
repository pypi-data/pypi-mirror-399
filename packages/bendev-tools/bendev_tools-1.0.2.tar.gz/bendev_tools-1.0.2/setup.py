from setuptools import setup, find_packages

setup(
    name="bendev_tools",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[],
    description= "A simple math operations library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = ">3.6",
)