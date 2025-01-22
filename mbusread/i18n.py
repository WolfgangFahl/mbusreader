"""
Created on 2025-01-22

@author: wf
"""


class I18n:
    """
    Simple internationalization class for message handling
    """

    MESSAGES = {
        "en": {
            "using_test_data": "Using test data...",
            "reading_data": "Reading data",
            "no_data_received": "No data received from serial port.",
            "read_data_hex": "Read data (hex): {}",
            "serial_error": "Serial communication error in {}: {}",
            "wake_up_started": "Wake-up sequence started ...",
            "wake_up_complete": "Wake-up sequence completed",
            "sending_request": "Sending M-Bus request...",
            "response_received": "Response received: {}",
        },
        "de": {
            "using_test_data": "Verwende Testdaten...",
            "reading_data": "Daten lesen",
            "no_data_received": "Keine Daten vom seriellen Port empfangen.",
            "read_data_hex": "gelesene Daten (hex): {}",
            "serial_error": "Fehler bei der seriellen Kommunikation in {}: {}",
            "wake_up_started": "Aufwecksequenz gestartet ...",
            "wake_up_complete": "Aufwecksequenz abgeschlossen",
            "sending_request": "Sende M-Bus Anfrage...",
            "response_received": "Antwort empfangen: {}",
        },
    }

    def __init__(self, language: str = "en"):
        self.language = language if language in self.MESSAGES else "en"

    def get(self, key: str, *args) -> str:
        """Get localized message with optional formatting"""
        message = self.MESSAGES[self.language].get(key, key)
        return message.format(*args) if args else message
