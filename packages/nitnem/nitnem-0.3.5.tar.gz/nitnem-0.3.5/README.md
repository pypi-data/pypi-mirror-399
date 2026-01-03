# nitnem

[![PyPI](https://img.shields.io/pypi/v/nitnem.svg)](https://pypi.org/project/nitnem/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/nitnem?include_prereleases&label=changelog)](https://github.com/sukhbinder/nitnem/releases)
[![Tests](https://github.com/sukhbinder/nitnem/actions/workflows/test.yml/badge.svg)](https://github.com/sukhbinder/nitnem/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/nitnem/blob/master/LICENSE)

Nitnem using python for Mac , Windows and Rashberry Pi.

For rashberry pi, this uses `omxplayer`, On mac it uses `afplay` and on windows it will use **afplay-win**

Nitnem Sahib (literally Daily Routine) is a collection of Sikh hymns (Gurbani) to be read minimally 3 different times of the day.

Read this blog post for [a background on this app](https://sukhbinder.wordpress.com/2024/12/09/nitnem/)

## Installation

Install this tool using `pip`:
```bash
pip install nitnem
```
## Usage

For help, run:
```bash
nitnem --help
```
You can also use:
```bash
python -m nitnem --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd nitnem
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
