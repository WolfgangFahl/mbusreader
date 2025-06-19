"""
Created on 2025-01-22
M-Bus configuration Classes to be read from configuration files e.g. YAML encoded
@author: wf
"""

import os
from dataclasses import field
from typing import Dict
from urllib.parse import quote

from basemkit.yamlable import lod_storable


# from ngwidgets.widgets import Link
# to avoid dependency here is a redundant copy
class Link:
    """
    a link
    """

    red = "color: red;text-decoration: underline;"
    blue = "color: blue;text-decoration: underline;"

    @staticmethod
    def create(
        url, text, tooltip=None, target=None, style: str = None, url_encode=False
    ):
        """
        Create a link for the given URL and text, with optional URL encoding.

        Args:
            url (str): The URL.
            text (str): The link text.
            tooltip (str): An optional tooltip.
            target (str): Target attribute, e.g., _blank for opening the link in a new tab.
            style (str): CSS style to be applied.
            url_encode (bool): Flag to indicate if the URL needs encoding. default: False

        Returns:
            str: HTML anchor tag as a string.
        """
        if url_encode:
            url = quote(url)

        title = "" if tooltip is None else f" title='{tooltip}'"
        target = "" if target is None else f" target='{target}'"
        if style is None:
            style = Link.blue
        style = f" style='{style}'"
        link = f"<a href='{url}'{title}{target}{style}>{text}</a>"
        return link


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

    Note on wakeup timing:
    The M-Bus standard formula suggests 33 bytes per 300 baud with
    start+8data+stop = 10 bits. However, we use configured pattern repetitions:
    - Default is 528 times (0x55)
    - Ultramaxx needs 1056 times (66 lines * 16 bytes)
    The total time includes sending these patterns at the given baudrate
    plus a fixed delay time.
    """

    model: str
    title: str = ""
    url: str = ""
    doc_url: str = ""
    has_echo: bool = False
    wakeup_pattern: str = "55"
    wakeup_times: int = 528  # Number of pattern repetitions
    wakeup_delay: float = 0.35  # secs
    messages: Dict[str, MBusMessage] = field(default_factory=dict)

    def wakeup_time(self, baudrate: int = 2400) -> float:
        """Calculate total wakeup time based on pattern repetitions"""
        secs = (self.wakeup_times * len(bytes.fromhex(self.wakeup_pattern))) / (
            baudrate / 10
        ) + self.wakeup_delay
        return secs

    def as_html(self) -> str:
        """Generate HTML representation of the device including wakeup info"""
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
        wakeup_html = f"""wakeup: {self.wakeup_pattern} = {self.wakeup_times}×0x{self.wakeup_pattern} ({self.wakeup_time(2400):.2f}s incl. {self.wakeup_delay}s delay)"""
        markup = f"""{mfr_html} → {device_link}{doc_link}<br>
{wakeup_html}"""
        return markup


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
