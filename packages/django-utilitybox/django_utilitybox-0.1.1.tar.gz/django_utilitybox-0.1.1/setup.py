from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '0.1.1'
DESCRIPTION = '...'
PACKAGE_NAME = 'django_utilitybox'
AUTHOR = 'Jose Angel Colin Najera'
EMAIL = 'josecolin99@gmail.com'
GITHUB_URL = 'https://github.com/Josecolin99/...'

setup(
    name = PACKAGE_NAME,
    packages = find_packages(),
    entry_points={
        "console_scripts": [
            "djangoutilitycmd=dj_utilitybox.__main__:main"
        ]
    },
    version = VERSION,
    license='MIT',
    description = DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    author = AUTHOR,
    author_email = EMAIL,
    url = GITHUB_URL,
    keywords = [
    ],
    install_requires=[
        "Django>=4.2",                # o la versión mínima que uses
        "djangorestframework>=3.14.0",
        "termcolor>=2.4.0"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)