"""
Created on 2025-01-24
based on https://github.com/ganehag/pyMeterBus/discussions/40

@author: Thorsten1982,wf

"""

import binascii
import time
from typing import Optional

import serial

from mbusread.i18n import I18n
from mbusread.logger import Logger
from mbusread.mbus_config import Device, MBusConfig, MBusIoConfig


class MBusReader:
    """Reader for Meter Bus data"""

    def __init__(
        self,
        device: Device,
        io_config: Optional[MBusIoConfig] = None,
        i18n: I18n = None,
        debug: bool = False,
    ):
        """
        Initialize MBusReader with configuration
        """
        self.debug = debug
        self.device = device
        self.logger = Logger.setup_logger(debug=debug)
        self.io_config = io_config or MBusIoConfig
        if i18n is None:
            i18n = I18n.default()
        self.i18n = i18n
        self.ser = self._setup_serial()

    def _setup_serial(self) -> serial.Serial:
        """Initialize serial connection"""
        ser = serial.Serial(
            port=self.io_config.serial_device,
            baudrate=self.io_config.initial_baudrate,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=self.io_config.timeout,
        )
        return ser

    def show_echo(self, msg: str, echo: str, echo_display_len: int = 32):
        if echo != msg:
            # Truncate to first echo_display_len bytes for readability
            sent_hex = msg[:echo_display_len].hex()
            echo_hex = echo[:echo_display_len].hex()
            warn_msg = f"""Echo mismatch!  Sent {len(msg)} Repl {len(echo)}
Sent={sent_hex}
Repl={echo_hex}"""
            self.logger.warning(warn_msg)
        else:
            self.logger.debug(f"Echo matched: {len(echo)} bytes")

    def ser_write(self, msg: bytes, info: str, echo_display_len: int = 16) -> None:
        """
        Writes a message to the serial port and validates the echo.

        Args:
            msg (bytes): The message to write as a byte string.
            info (str): The log message key for identifying the operation.

        Logs:
            A warning if the echo does not match the sent message.
            A debug message if the echo matches.
        """
        self.logger.info(self.i18n.get(info))
        self.ser.write(msg)
        self.ser.flush()
        if self.device.has_echo:
            # Check and validate echo
            echo = self.ser.read(len(msg))
            self.show_echo(msg, echo, echo_display_len)

    def wake_up(self, device: Device) -> None:
        """Perform the wakeup sequence based on device configuration"""
        try:
            pattern = bytes.fromhex(device.wakeup_pattern)
            times = device.wakeup_times
            sleep_time = device.wakeup_delay

            self.ser_write(pattern * times, "wake_up_started")
            time.sleep(sleep_time)
            self.ser.parity = serial.PARITY_EVEN
            self.logger.info(self.i18n.get("wake_up_complete"))
        except serial.SerialException as e:
            self.logger.error(self.i18n.get("serial_error", "wake_up", str(e)))

    def get_data(self, read_data_msg_key: str = "read_data") -> Optional[bytes]:
        """Get data from the M-Bus device"""
        try:
            if read_data_msg_key not in self.device.messages:
                raise ValueError(f"Message {read_data_msg_key} not found")

            self.wake_up(self.device)
            read_data = bytes.fromhex(self.device.messages[read_data_msg_key].hex)
            self.ser_write(read_data, "reading_data")

            result = self.ser.read(620)
            if not result:
                self.logger.warning(self.i18n.get("no_data_received"))
                return None

            byte_array_hex = binascii.hexlify(result)
            self.logger.info(self.i18n.get("read_data_hex", byte_array_hex.decode()))
            return result

        except serial.SerialException as e:
            self.logger.error(self.i18n.get("serial_error", "get_data", str(e)))
            return None

    def send_mbus_request(self, msg_id: str) -> None:
        """Send an M-Bus request to the device"""
        try:
            if msg_id not in self.device.messages:
                raise ValueError(f"Message {msg_id} not found in device configuration")

            request = bytes.fromhex(self.device.messages[msg_id].hex)
            self.logger.info(self.i18n.get("sending_request"))
            self.ser.write(request)
        except serial.SerialException as e:
            self.logger.error(
                self.i18n.get("serial_error", "send_mbus_request", str(e))
            )

    def read_response(self, buffer_size: int = 256) -> Optional[bytes]:
        """Read the response from the device"""
        try:
            response = self.ser.read(buffer_size)
            if response:
                hex_response = " ".join(format(b, "02x") for b in response)
                self.logger.info(self.i18n.get("response_received", hex_response))
                return response
            return None
        except serial.SerialException as e:
            self.logger.error(self.i18n.get("serial_error", "read_response", str(e)))
            return None

    def close(self) -> None:
        """Close the serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
