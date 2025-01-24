#!/usr/bin/env python3
# M-Bus Reader Implementation
# Date: 2025-01-22

import argparse

from mbusread.i18n import I18n
from mbusread.mbus_config import MBusConfig, MBusIoConfig
from mbusread.mbus_mqtt import MBusMqtt
from mbusread.mbus_reader import MBusReader


def main():
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
        "-D", "--device", default="cf_echo_ii", help="Device type [default: %(default)s]"
    )
    parser.add_argument("-m", "--message", help="Message ID to send [default: %(default)s]")
    parser.add_argument("--mqtt", action="store_true", help="Enable MQTT publishing")
    parser.add_argument(
        "--lang",
        choices=["en", "de"],
        default="en",
        help="Language for messages (default: en)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    i18n = I18n.default()
    i18n.language=args.lang
    mbus_config = MBusConfig.get(args.config)
    io_config = MBusIoConfig.load_from_yaml_file(args.io_config)

    reader = MBusReader(mbus_config, io_config, i18n=i18n)
    try:
        if args.message:
            reader.send_mbus_request(args.message)
            data = reader.read_response()
        else:
            data = reader.get_data()

        if data and args.mqtt:
            mqtt_handler = MBusMqtt(io_config)
            mqtt_handler.publish(data)
    finally:
        reader.close()
