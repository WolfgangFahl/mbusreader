"""
Created on 2025-01-24

@author: wf
"""

from unittest.mock import MagicMock, patch

import serial
from ngwidgets.basetest import Basetest

from mbusread.i18n import I18n
from mbusread.mbus_config import (
    Device,
    Manufacturer,
    MBusConfig,
    MBusIoConfig,
    MBusMessage,
)
from mbusread.mbus_reader import MBusReader


class TestMBusReader(Basetest):
    """
    test MBusParser
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.examples_path = MBusConfig.examples_path()

        # Mock the serial connection
        self.mock_serial_patcher = patch("serial.Serial")
        self.mock_serial = self.mock_serial_patcher.start()
        self.mock_ser = MagicMock()
        self.mock_serial.return_value = self.mock_ser

        # Initialize configurations
        self.config = MBusConfig.get(self.examples_path + "/mbus_config.yaml")
        self.io_config = MBusIoConfig()
        self.i18n = I18n.default()
        self.manufacturer = list(self.config.manufacturers.values())[0]
        self.devices = list(self.manufacturer.devices.values())

    def tearDown(self):
        """Clean up after tests"""
        self.mock_serial_patcher.stop()

   
    def get_device(self, index:int=0) -> Device:
        """Get test device by index"""
        return self.devices[index]

    def test_wake_up_pattern(self):
        """Test wake up patterns for all devices"""
        for device in self.devices:
            reader = MBusReader(self.config, self.io_config, self.i18n)
            expected_pattern = bytes.fromhex('55') * device.wakeup_times
            self.mock_ser.read.return_value = expected_pattern
            reader.wake_up(device)
            self.mock_ser.write.assert_called_with(expected_pattern)

    def test_ultramaxx_wake_up(self):
        """Test wake up sequence for UltraMaxx"""
        reader = MBusReader(self.config, self.io_config, self.i18n)
        device = self.config.manufacturers['allmess'].devices['ultramaxx']
        expected_pattern = bytes.fromhex('55') * 1056
        self.mock_ser.read.return_value = expected_pattern  # Mock correct echo
        reader.wake_up(device)
        self.mock_ser.write.assert_called_with(expected_pattern)


    def test_get_data_no_response(self):
        """Test get_data when no response is received"""
        reader = MBusReader(self.config, self.io_config, self.i18n)
        self.mock_ser.read.return_value = b""

        result = reader.get_data(device=self.get_device())
        self.assertIsNone(result)

    def test_send_mbus_request(self):
        """Test sending M-Bus request message"""
        reader = MBusReader(self.config, self.io_config, self.i18n)
        reader.device_id = "allmess"
        reader.device = "ultramaxx"

        reader.send_mbus_request("msg1")
        expected_request = bytes.fromhex("68 03 03 68 53 fe a6 f7 16")
        self.mock_ser.write.assert_called_with(expected_request)

    def test_read_response(self):
        """Test reading response from device"""
        reader = MBusReader(self.config, self.io_config, self.i18n)
        test_response = bytes.fromhex("68 1c 1c 68 08 00 72")
        self.mock_ser.read.return_value = test_response

        result = reader.read_response()
        self.assertEqual(result, test_response)
    
    def test_echo_mismatch(self):
        """Test echo mismatch formatting with a longer pattern"""
        reader = MBusReader(self.config, self.io_config, self.i18n)
        test_msg = bytes.fromhex("55" * 528)  # Full wake-up pattern
        wrong_response = bytes.fromhex("AA" * 528)
        self.mock_ser.read.return_value = wrong_response
       
        # Capture log output
        with self.assertLogs(level='WARNING') as cm:
            reader.ser_write(test_msg, "wake_up_started")
            expected_msg = "Echo mismatch! First 16 bytes: Sent=0x55555555555555555555555555555555..., Received=0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa..."
            self.assertIn(expected_msg, cm.output[0])