"""
Created on 2025-01-22
see also
https://github.com/ganehag/pyMeterBus/discussions/40
@author: Thorsten1982, wf
"""

import json
import re
import traceback
from typing import Optional

import meterbus
from meterbus.telegram_short import TelegramShort

from mbusread.logger import Logger


class MBusParser:
    """
    parse MBus data
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = Logger.setup_logger(debug=debug)

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

    def extract_frame(self, data: bytes) -> Optional[bytes]:
        """Extract valid M-Bus frame between start (0x68) and end (0x16) bytes"""
        start_byte = b"\x68"
        end_byte = b"\x16"
        result = None
        status = "❌"

        if data:
            try:
                start_idx = data.index(start_byte)
                next_end = start_idx + 1
                while (end_idx := data.find(end_byte, next_end)) != -1:
                    status = "⚠️"
                    frame_len = end_idx - start_idx - 5
                    if frame_len >= 3:  # minimum length for 68 L L
                        l1 = data[start_idx + 1]
                        l2 = data[start_idx + 2]
                        if l1 == l2 and l1 == frame_len:  # length field matches data length
                            result = data[start_idx : end_idx + 1]
                            status = "✅"
                            break
                    next_end = end_idx + 1
            except ValueError:
                pass

        self.logger.debug(
            f"Frame extraction {status}: {result.hex() if result else 'None'}"
        )
        return result