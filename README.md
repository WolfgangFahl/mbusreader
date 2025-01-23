# mbusreader
Meterbus reader

[![pypi](https://img.shields.io/pypi/pyversions/mbusreader)](https://pypi.org/project/mbusreader/)
[![Github Actions Build](https://github.com/WolfgangFahl/mbusreader/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/mbusreader/actions/workflows/build.yml)
[![PyPI Status](https://img.shields.io/pypi/v/mbusreader.svg)](https://pypi.python.org/pypi/mbusreader/)
[![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/mbusreader.svg)](https://github.com/WolfgangFahl/mbusreader/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/WolfgangFahl/mbusreader.svg)](https://github.com/WolfgangFahl/mbusreader/issues/?q=is%3Aissue+is%3Aclosed)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://WolfgangFahl.github.io/mbusreader/)
[![License](https://img.shields.io/github/license/WolfgangFahl/mbusreader.svg)](https://www.apache.org/licenses/LICENSE-2.0)

## Docs and Tutorials
[Wiki](https://wiki.bitplan.com/index.php/MBus_Reader)

# Introduction
## Demo
* [mbus viewer](https://mbus.bitplan.com)

## MBus Viewer
See also [Live M-Bus datagram decoder](https://dev-lab.github.io/tmbus/tmbus.htm)

The MBus-Viewer is a Python-based tool for decoding
M-Bus datagrams/telegrams from consumption meters and other
compatible devices. It leverages the `pyMeterBus` library
to convert these datagrams into JSON and displays
the parsed results for analysis and debugging.

## MBus Reader
The MBus Reader is for reading M-Bus devices and optionally integration into
your favorite home automation by forwarding the JSON results e.g. via [MQTT](https://en.wikipedia.org/wiki/MQTT).

## Screenshot
![Screenshot](https://github.com/user-attachments/assets/ca0a41ae-6513-496c-b3ce-b3a892f66d3f)
