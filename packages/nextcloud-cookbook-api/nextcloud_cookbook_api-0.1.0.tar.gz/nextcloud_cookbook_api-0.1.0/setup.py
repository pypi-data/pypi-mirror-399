from setuptools import find_packages, setup

from nextcloud_cookbook_api import __version__

with open("Readme.md") as f:
    long_description = f.read()

setup(
    name="nextcloud_cookbook_api",
    version=__version__,
    author="infinityofspace",
    url="https://github.com/infinityofspace/nextcloud_cookbook_api",
    description="Python API client for nextcloud cookbook app API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10",
    install_requires=["requests>=2.0,<3.0", "pydantic>=2.0,<3.0", "setuptools>=41.6.0"],
)
