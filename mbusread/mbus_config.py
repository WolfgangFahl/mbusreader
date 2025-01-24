"""
Created on 2025-01-22



@author: wf
"""

import os
from dataclasses import field
from typing import Dict

from ngwidgets.widgets import Link
from ngwidgets.yamlable import lod_storable


@lod_storable
class MBusIoConfig:
    """Configuration data class for M-Bus reader"""

    serial_device: str = "/dev/ttyUSB0"
    initial_baudrate: int = 2400
    timeout: float = 10.0


@lod_storable
class MqttConfig:
    """MQTT configuration"""

    broker: str = "localhost"
    port: int = 1883
    username: str = None
    password: str = None
    topic: str = "mbus/data"


@lod_storable
class MBusMessage:
    """
    An M-Bus message
    """

    name: str
    title: str
    hex: str
    valid: bool = False

    def as_html(self) -> str:
        device_html = self.device.as_html() if hasattr(self, "device") else self.did
        example_text = f"{self.name}: {self.title}" if self.title else self.name
        return f"{device_html} → {example_text}"


@lod_storable
class Device:
    """
    A device class for M-Bus devices storing manufacturer reference
    """

    model: str
    title: str = ""  # Optional full product title
    url: str = ""  # optional device url
    doc_url: str = ""  # Documentation URL
    wakeup_pattern: str = None
    wakeup_time: float = 2.2  # secs
    wakeup_delay: float = 0.35  # secs
    messages: Dict[str, MBusMessage] = field(default_factory=dict)

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
class Manufacturer:
    """
    A manufacturer of M-Bus devices
    """

    name: str
    url: str
    country: str = "Germany"  # Most M-Bus manufacturers are German
    devices: Dict[str, Device] = field(default_factory=dict)

    def as_html(self) -> str:
        return (
            Link.create(url=self.url, text=self.name, target="_blank")
            if self.url
            else self.name
        )


@lod_storable
class MBusConfig:
    """
    Manages M-Bus manufacture/devices/message hierarchy
    """

    manufacturers: Dict[str, Manufacturer] = field(default_factory=dict)

    @classmethod
    def get(cls, yaml_path: str = None) -> "MBusConfig":
        if yaml_path is None:
            yaml_path = cls.examples_path() + "/mbus_config.yaml"

        # Load raw YAML data
        mbus_config = cls.load_from_yaml_file(yaml_path)
        mbus_config.relink()
        return mbus_config

    def relink(self):
        """
        Link objects in the manufacturer/device/message hierarchy
        """
        for manufacturer in self.manufacturers.values():
            for _device_id, device in manufacturer.devices.items():
                device.manufacturer = manufacturer
                for _message_id, message in device.messages.items():
                    message.device = device

    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../mbusread_examples")
        path = os.path.abspath(path)
        return path
