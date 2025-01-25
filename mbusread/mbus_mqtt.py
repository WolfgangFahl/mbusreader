"""
Created on 2025-01-24
based on https://github.com/ganehag/pyMeterBus/discussions/40

@author: Thorsten1982,wf
"""

import logging
import time
import json
import paho.mqtt.client as mqtt

from mbusread.mbus_config import MqttConfig
from typing import Dict

class MBusMqtt:
    """MQTT handler for M-Bus data"""

    def __init__(self, config: MqttConfig):
        self.config = config
        self.logger = logging.getLogger("MBusMqtt")

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "MBusMqtt":
        config = cls.load_from_yaml_file(yaml_path)
        mqtt
        return mqtt

    def publish(self, record:Dict):
        """Publish M-Bus data via MQTT"""
        client = mqtt.Client()
        if self.config.username:
            client.username_pw_set(self.config.username, self.config.password)

        try:
            client.connect(self.config.broker, self.config.port, 60)
            client.loop_start()
            json_str = json.dumps(record, indent=2)
            client.publish(self.config.topic, json_str)
            time.sleep(1)
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            self.logger.error(f"MQTT error: {str(e)}")
