"""
Created on 2025-01-22

@author: wf
"""

import os
from dataclasses import dataclass, field
from typing import Dict

from ngwidgets.widgets import Link
from ngwidgets.yamlable import lod_storable


@dataclass
class MBusConfig:
    """Configuration data class for M-Bus reader"""

    serial_device: str = "/dev/ttyUSB0"
    baudrate: int = 2400
    timeout: float = 10.0
    debug: bool = False
    language: str = "en"


@lod_storable
class Manufacturer:
    """
    A manufacturer of M-Bus devices
    """

    name: str
    url: str
    country: str = "Germany"  # Most M-Bus manufacturers are German

    def as_html(self) -> str:
        return (
            Link.create(url=self.url, text=self.name, target="_blank")
            if self.url
            else self.name
        )


@lod_storable
class Device:
    """
    A device class for M-Bus devices storing manufacturer reference
    """

    mid: str  # manufacturer id reference
    model: str
    title: str = ""  # Optional full product title
    url: str = ""  # optional device url
    doc_url: str = ""  # Documentation URL
    # manufacturer: Manufacturer - set on relink

    def as_html(self) -> str:
        title = self.title if self.title else self.model
        device_link = (
            Link.create(url=self.url, text=title, target="_blank")
            if self.doc_url
            else title
        )
        doc_link = (
            Link.create(url=self.doc_url, text="📄", target="_blank")
            if self.doc_url
            else ""
        )
        mfr_html = (
            self.manufacturer.as_html() if hasattr(self, "manufacturer") else self.mid
        )
        return f"{mfr_html} → {device_link}{doc_link}"


@lod_storable
class MBusExample:
    """
    An M-Bus example storing device reference
    """

    did: str  # device id reference
    name: str
    title: str
    hex: str
    valid: bool = False
    # device: Device - set on relink

    def as_html(self) -> str:
        device_html = self.device.as_html() if hasattr(self, "device") else self.did
        example_text = f"{self.name}: {self.title}" if self.title else self.name
        return f"{device_html} → {example_text}"


@lod_storable
class MBusExamples:
    """
    Manages M-Bus devices and their examples with separate dictionaries for
    manufacturers, devices and examples
    """

    manufacturers: Dict[str, Manufacturer] = field(default_factory=dict)
    devices: Dict[str, Device] = field(default_factory=dict)
    examples: Dict[str, MBusExample] = field(default_factory=dict)

    @classmethod
    def get(cls, yaml_path: str = None) -> "MBusExamples":
        """
        Load and dereference M-Bus examples from YAML

        Args:
            yaml_path: Path to YAML file (defaults to examples_path/mbus_examples.yaml)

        Returns:
            MBusExamples instance with dereferenced objects
        """
        if yaml_path is None:
            yaml_path = cls.examples_path() + "/mbus_examples.yaml"

        # Load raw YAML data
        mbus_examples = cls.load_from_yaml_file(yaml_path)
        mbus_examples.relink()
        return mbus_examples

    def relink(self):
        """
        Reestablish object references between manufacturers, devices and examples
        """
        # Dereference manufacturers in devices
        for device_id, device in self.devices.items():
            if device.mid in self.manufacturers:
                device.manufacturer = self.manufacturers[device.mid]
            else:
                raise KeyError(
                    f"Manufacturer '{device.mid}' not found for device '{device_id}'"
                )

        # Dereference devices in examples
        for example_id, example in self.examples.items():
            if example.did in self.devices:
                example.device = self.devices[example.did]
            else:
                raise KeyError(
                    f"Device '{example.did}' not found for example '{example_id}'"
                )

    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../mbusread_examples")
        path = os.path.abspath(path)
        return path
