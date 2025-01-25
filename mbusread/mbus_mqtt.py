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
    def __init__(self, config: MqttConfig):
        self.config = config
        self.logger = logging.getLogger("MBusMqtt")
        self.client = mqtt.Client()
        if self.config.username:
            self.client.username_pw_set(self.config.username, self.config.password)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT broker")
        else:
            self.logger.error(f"Failed to connect, code: {rc}")

    def on_publish(self, client, userdata, mid):
        self.logger.info(f"Data published to MQTT (MID: {mid})")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.logger.warning(f"Disconnected, code: {rc}. Trying to reconnect...")
            client.reconnect()
        else:
            self.logger.info("Successfully disconnected")

    def publish(self, record: Dict):
        try:
            self.client.connect(self.config.broker, self.config.port, 60)
            self.client.loop_start()
            json_str = json.dumps(record, indent=2)
            self.client.publish(self.config.topic, json_str)
            time.sleep(1)
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            self.logger.error(f"MQTT error: {str(e)}")