"""
Created on 2025-01-25

@author: wf
"""
import json
from unittest.mock import patch

from ngwidgets.basetest import Basetest
from mbusread.mbus_config import MqttConfig,MBusConfig
from mbusread.mbus_mqtt import MBusMqtt

class TestMqtt(Basetest):
    """Test MQTT functionality"""

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.examples_path = MBusConfig.examples_path()
        self.mock_client = self.mock_mqtt_client()
        self.mqtt_config = MqttConfig(
            broker="localhost",
            port=1883,
            topic="test/topic"
        )

    def mock_mqtt_client(self):
        """Set up mock MQTT client"""
        mqtt_patcher = patch('paho.mqtt.client.Client')
        mock_client = mqtt_patcher.start()
        self.addCleanup(mqtt_patcher.stop)
        return mock_client

    def test_mqtt_publish(self):
        """Test MQTT publishing"""
        mqtt_handler = MBusMqtt(self.mqtt_config)
        test_data = {"test": "data"}
        mqtt_handler.publish(test_data)

        self.mock_client.assert_called_once()
        mock_client_instance = self.mock_client.return_value
        mock_client_instance.connect.assert_called_with(
            "localhost", 1883, 60
        )
        mock_client_instance.publish.assert_called_with(
            "test/topic",
            json.dumps(test_data, indent=2)
        )

    def test_mqtt_auth(self):
        """Test MQTT with authentication"""
        self.mqtt_config.username = "user"
        self.mqtt_config.password = "pass"
        mqtt_handler = MBusMqtt(self.mqtt_config)
        mqtt_handler.publish({"test": "data"})

        mock_client_instance = self.mock_client.return_value
        mock_client_instance.username_pw_set.assert_called_with(
            "user", "pass"
        )
