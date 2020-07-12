import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="aiomangadex",
    version="0.3.0",
    description="A simple asynchronous API wrapper for mangadex.org.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lukesaltweather/aiomangadex",
    author="lukesaltweather",
    author_email="lukesaltweather@gmail.com",
    license="Apache License 2.0",
    classifiers=[!
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 3 - Alpha'
    ],
    packages=["aiomangadex"],
    include_package_data=True,
    install_requires=["aiohttp"]
)
