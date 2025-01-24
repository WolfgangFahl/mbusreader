"""
Created on 2025-01-22
@author: wf
"""

import json
import re
import traceback

import meterbus
from meterbus.telegram_short import TelegramShort


class MBusParser:
    """
    parse MBus data
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def fromhex(self, x, base=16):
        """Convert hex string to integer"""
        return int(x, base)

    def get_frame_json(self, frame):
        """
        Workarounds for JSON bugs in pyMeterBus
        """
        if isinstance(frame, TelegramShort):
            # Handle serialization explicitly for TelegramShort
            interpreted_data = frame.interpreted
            json_str = json.dumps(
                interpreted_data, sort_keys=True, indent=2, default=str
            )
        elif hasattr(frame, "to_JSON"):
            json_str = frame.to_JSON()
        else:
            # Fallback to basic frame info
            data = {
                "header": {
                    "start": frame.header.startField.parts[0],
                    "length": len(frame.body.bodyHeader.ci_field.parts) + 2,
                    "control": frame.header.cField.parts[0],
                    "address": frame.header.aField.parts[0],
                },
                "body": {"ci_field": frame.body.bodyHeader.ci_field.parts[0]},
            }
            json_str = json.dumps(data)
        return json_str

    def parse_mbus_frame(self, hex_data):
        """
        Parse M-Bus hex data and return mbus frame
        Returns tuple of (error_msg, mbus_frame)
        """
        frame = None
        error_msg = None
        try:
            filtered_data = "".join(char for char in hex_data if char.isalnum())
            data = list(map(self.fromhex, re.findall("..", filtered_data)))
            frame = meterbus.load(data)
        except Exception as ex:
            error_type = type(ex).__name__
            error_msg = f"Error parsing M-Bus data: {error_type}: {str(ex)}"
            if self.debug:
                traceback.format_exception(ex)
        return error_msg, frame
