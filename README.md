# mbusreader
Meterbus reader

| | |
| :--- | :--- |
| **PyPi** | [![PyPI Status](https://img.shields.io/pypi/v/mbusreader.svg)](https://pypi.python.org/pypi/mbusreader/) [![License](https://img.shields.io/github/license/WolfgangFahl/mbusreader.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![pypi](https://img.shields.io/pypi/pyversions/mbusreader)](https://pypi.org/project/mbusreader/) [![format](https://img.shields.io/pypi/format/mbusreader)](https://pypi.org/project/mbusreader/) [![downloads](https://img.shields.io/pypi/dd/mbusreader)](https://pypi.org/project/mbusreader/) |
| **GitHub** | [![Github Actions Build](https://github.com/WolfgangFahl/mbusreader/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/mbusreader/actions/workflows/build.yml) [![Release](https://img.shields.io/github/v/release/WolfgangFahl/mbusreader)](https://github.com/WolfgangFahl/mbusreader/releases) [![Contributors](https://img.shields.io/github/contributors/WolfgangFahl/mbusreader)](https://github.com/WolfgangFahl/mbusreader/graphs/contributors) [![Last Commit](https://img.shields.io/github/last-commit/WolfgangFahl/mbusreader)](https://github.com/WolfgangFahl/mbusreader/commits/) [![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/mbusreader.svg)](https://github.com/WolfgangFahl/mbusreader/issues) [![GitHub closed issues](https://img.shields.io/github/issues-closed/WolfgangFahl/mbusreader.svg)](https://github.com/WolfgangFahl/mbusreader/issues/?q=is%3Aissue+is%3Aclosed) |
| **Code** | [![style-black](https://img.shields.io/badge/%20style-black-000000.svg)](https://github.com/psf/black) [![imports-isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/) |
| **Docs** | [![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://WolfgangFahl.github.io/mbusreader/) [![formatter-docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter) [![style-google](https://img.shields.io/badge/%20style-google-3666d6.svg)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) |
## Docs and Tutorials
[Wiki](https://wiki.bitplan.com/index.php/MBus_Reader)

# Introduction
## Demo
* [mbus viewer](https://mbus.bitplan.com)

## MBus Viewer
See also [Live M-Bus datagram decoder](https://dev-lab.github.io/tmbus/tmbus.htm)

The MBus-Viewer is a Python-based tool for decoding
M-Bus datagrams/telegrams from consumption meters and other
compatible devices. It leverages the [pyMeterBus](https://github.com/ganehag/pyMeterBus) library
to convert these datagrams into JSON and displays
the parsed results for analysis and debugging.

## MBus Reader
The MBus Reader is for reading M-Bus devices and optionally integration into
your favorite home automation by forwarding the JSON results e.g. via [MQTT](https://en.wikipedia.org/wiki/MQTT).

## Screenshot
![Screenshot](https://github.com/user-attachments/assets/ca0a41ae-6513-496c-b3ce-b3a892f66d3f)
