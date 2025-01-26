"""
Created on 2025-01-17

@author: wf
"""

import json

from ngwidgets.basetest import Basetest

from mbusread.i18n import I18n
from mbusread.mbus_config import Device, Manufacturer, MBusConfig, MBusMessage
from mbusread.mbus_viewer import MBusParser


class TestMBusParser(Basetest):
    """
    test MBusParser
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.examples_path = MBusConfig.examples_path()

    def test_i18n(self):
        """
        test the internationalization
        """
        i18n = I18n.default()

        # Test English messages
        self.assertEqual("Using test data...", i18n.get("using_test_data"))
        self.assertEqual(
            "Serial communication error in test: error",
            i18n.get("serial_error", "test", "error"),
        )

        # Test German messages
        i18n.language = "de"
        self.assertEqual("Verwende Testdaten...", i18n.get("using_test_data"))
        self.assertEqual(
            "Fehler bei der seriellen Kommunikation in test: error",
            i18n.get("serial_error", "test", "error"),
        )

        # Test fallback to key for unknown message
        self.assertEqual("unknown_key", i18n.get("unknown_key"))

        # Test fallback to English for unknown language
        i18n.language = "fr"
        self.assertEqual("Using test data...", i18n.get("using_test_data"))

    def test_mbus_parser(self):
        """
        Test examples from MBusParser class
        """
        mbus_parser = MBusParser(debug=self.debug)
        mbus_config = MBusConfig.get()

        for manufacturer in mbus_config.manufacturers.values():
            for device in manufacturer.devices.values():
                for msg_id, message in device.messages.items():
                    if not message.hex:
                        if self.debug:
                            print(f"{message.name}: ⚪ no hex data")
                        continue

                    error_msg, frame = mbus_parser.parse_mbus_frame(message.hex)
                    if self.debug:
                        marker = "✗" if error_msg else "✓"
                        print(f"{message.name} {marker}")
                        if error_msg:
                            print(f" {error_msg}")
                        else:
                            json_str = mbus_parser.get_frame_json(frame)
                            json_data = json.loads(json_str)
                            print(json.dumps(json_data, indent=2))

                    if message.hex:  # only assert for messages with hex data
                        if message.valid:
                            self.assertIsNone(
                                error_msg, f"Failed to parse {message.name}"
                            )
                            self.assertIsInstance(json_data, dict)

    def test_extract_frame(self):
        """Test frame extraction from binary data"""
        mbus_parser = MBusParser(debug=self.debug)
        hex_datas = [
            "684d4d680800722654832277040904360000000c78265483220406493500000c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200046d0d0c2c310227c80309fd0e2209fd0f470f00008d16",
            "684d4d680800728194362092261704fb0000000c788194362004060ea100000c14827636000b2d1400000b3b6400000a5a70050a5e72030b61811900046d20163a3102270b0709fd0e0709fd0f110f0000f816"
        ]
        for hex_data in hex_datas:
            test_data = bytes.fromhex(hex_data)

            # Test valid frame
            result = mbus_parser.extract_frame(test_data)
            self.assertIsNotNone(result)
            self.assertEqual(result.hex(), hex_data)



        # Test no start byte
        result = mbus_parser.extract_frame(b"\x00\x01\x02")
        self.assertIsNone(result)

        # Test no end byte
        result = mbus_parser.extract_frame(b"\x68\x01\x02")
        self.assertIsNone(result)

        # Test empty data
        result = mbus_parser.extract_frame(b"")
        self.assertIsNone(result)


    def test_create_mbus_examples(self):
        """
        Create MBus examples structure with manufacturers and their devices/messages
        """
        # Create manufacturer with devices
        manufacturer = Manufacturer(
            name="Allmess", url="https://www.allmess.de", country="Germany"
        )

        # Create devices with messages
        cf_echo = Device(
            model="CF Echo II",
            doc_url="https://www.allmess.de/fileadmin/multimedia/alle_Dateien/MA/MA_BA_12088-AC%20CF%20Echo%20II%20D%20TS1021_KL.pdf",
            messages={
                "basic_reading": MBusMessage(
                    name="Basic Reading",
                    title="Standard M-Bus reading",
                    hex="684d4d680800722654832277040904360000000c78265483220406493500000c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200046d0d0c2c310227c80309fd0e2209fd0f470f00008d16",
                    valid=True,
                ),
                "init": MBusMessage(
                    name="CF Echo II init write",
                    title="CF Echo II init",
                    hex="6803036873fea61716",
                    valid=True,
                ),
            },
        )

        ultramaxx = Device(
            model="UltraMaXX",
            title="Integral-MK UltraMaXX",
            doc_url="https://www.allmess.de/fileadmin/multimedia/alle_Dateien/DB/DB_P0012%20UltraMaXX_TS0219.pdf",
            messages={
                "init": MBusMessage(
                    name="CFUM init",
                    title="CFUM init",
                    hex="6803036853fea6f716",
                    valid=True,
                )
            },
        )

        manufacturer.devices = {"cf_echo_ii": cf_echo, "ultramaxx": ultramaxx}

        # Create MBusConfig with manufacturer
        mbus_config = MBusConfig(manufacturers={"allmess": manufacturer})

        # Save to YAML file
        yaml_path = "/tmp/mbus_config.yaml"
        mbus_config.save_to_yaml_file(yaml_path)
        if self.debug:
            print(f"Created YAML file at {yaml_path}")

        # Verify we can read it back
        loaded_config = MBusConfig.load_from_yaml_file(yaml_path)
        loaded_config.relink()

        # Test structure
        self.assertEqual(len(loaded_config.manufacturers), 1)
        allmess = loaded_config.manufacturers["allmess"]
        self.assertEqual(len(allmess.devices), 2)

        # Test device loading
        cf_echo = allmess.devices["cf_echo_ii"]
        self.assertEqual(len(cf_echo.messages), 2)
        self.assertEqual(cf_echo.manufacturer, allmess)

        # Test message loading
        for message in cf_echo.messages.values():
            self.assertEqual(message.device, cf_echo)
            self.assertTrue(message.valid)
