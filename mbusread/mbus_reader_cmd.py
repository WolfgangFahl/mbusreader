#!/usr/bin/env python3
# M-Bus Reader Implementation
# Date: 2025-01-22

import argparse

from mbusread.i18n import I18n
from mbusread.logger import Logger
from mbusread.mbus_config import MBusConfig, MBusIoConfig
from mbusread.mbus_mqtt import MBusMqtt, MqttConfig
from mbusread.mbus_parser import MBusParser
from mbusread.mbus_reader import MBusReader


class MBusCommunicator:
    """ """

    def __init__(self, args: argparse.Namespace):
        self.logger = Logger.setup_logger(args.debug)
        i18n = I18n.default()
        i18n.language = args.lang
        mbus_config = MBusConfig.get(args.config)
        io_config = MBusIoConfig.load_from_yaml_file(args.io_config)
        device = mbus_config.manufacturers[args.manufacturer].devices[args.device]
        self.mqtt_config = (
            MqttConfig.load_from_yaml_file(args.mqtt_config)
            if args.mqtt_config
            else None
        )

        self.reader = MBusReader(
            device=device, io_config=io_config, i18n=i18n, debug=args.debug
        )
        self.parser = MBusParser(debug=args.debug)

        pass

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="M-Bus Reader")
        parser.add_argument(
            "-c",
            "--config",
            default=MBusConfig.examples_path() + "/mbus_config.yaml",
            help="Config file path [default: %(default)s]",
        )
        parser.add_argument(
            "-i",
            "--io_config",
            default=MBusConfig.examples_path() + "/mbus_io_config.yaml",
            help="IO config file path [default: %(default)s]",
        )
        parser.add_argument(
            "-q",
            "--mqtt_config",
            default=MBusConfig.examples_path() + "/mqtt_config.yaml",
            help="MQTT config file path [default: %(default)s]",
        )

        parser.add_argument(
            "-D",
            "--device",
            default="cf_echo_ii",
            help="Device type [default: %(default)s]",
        )
        parser.add_argument(
            "-m", "--message", help="Message ID to send [default: %(default)s]"
        )
        parser.add_argument(
            "-M",
            "--manufacturer",
            default="allmess",
            help="Manufacturer ID [default: %(default)s]",
        )
        parser.add_argument(
            "--mqtt", action="store_true", help="Enable MQTT publishing"
        )
        parser.add_argument(
            "--lang",
            choices=["en", "de"],
            default="en",
            help="Language for messages (default: en)",
        )
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        return parser

    def work(self):
        try:
            if self.args.message:
                self.reader.send_mbus_request(self.args.message)
                raw_data = self.reader.read_response()
            else:
                raw_data = self.reader.get_data()
            frame = self.parser.extract_frame(raw_data)
            if not frame:
                self.logger.warning("No valid frame found in data")
                return None

            if frame and self.args.mqtt:
                mqtt_handler = MBusMqtt(self.mqtt_config)
                mqtt_handler.publish(frame)
        finally:
            self.reader.close()


def main():
    parser = MBusCommunicator.get_parser()
    args = parser.parse_args()
    communicator = MBusCommunicator(args)
    communicator.work
