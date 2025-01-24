"""
Created on 2025-01-22

@author: wf
"""

from dataclasses import field
from typing import Dict

from ngwidgets.yamlable import lod_storable

from mbusread.mbus_config import MBusConfig


@lod_storable
class I18n:
    """Simple internationalization class for message handling"""

    language: str = "en"
    messages: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "I18n":
        yaml_file = MBusConfig.examples_path() + "/i18n.yaml"
        i18n = cls.load_from_yaml_file(yaml_file)
        return i18n

    def get(self, key: str, *args) -> str:
        """Get localized message with optional formatting"""
        if self.language not in self.messages:
            self.language = "en"
        message = self.messages[self.language].get(key, key)
        formatted_message = message.format(*args) if args else message
        return formatted_message
