from dataclasses import dataclass, field
from typing import Callable, Dict, Generic, Optional, TypeVar

from nicegui import observables, ui

from mbusread.mbus_config import Device, Manufacturer, MBusConfig, MBusMessage
from mbusread.mbus_parser import MBusParser

T = TypeVar("T")


@dataclass
class RadioSelection(Generic[T]):
    """Generic radio button selection with type hints and improved structure"""

    title: str
    key_attr: str
    selection: Dict[str, T] = field(default_factory=dict)
    value: Optional[str] = None
    item: Optional[T] = None
    on_change: Optional[Callable[[T], None]] = None

    def __post_init__(self):
        self.radio = None
        self.label = None
        self.options = observables.ObservableDict()

    def setup(
        self, on_change: Optional[Callable[[T], None]] = None
    ) -> "RadioSelection[T]":
        """Initialize the radio selection UI components"""
        self.on_change = on_change
        with ui.column():
            self.label = ui.label(self.title).classes("font-bold text-lg")
            self.options = observables.ObservableDict()
            self._update_options()
            self.radio = ui.radio(
                options=list(self.options.keys()),
                on_change=self._handle_change,
                value=self.value,
            ).props("inline dense")
        return self

    def _update_options(self) -> None:
        """Update radio options with error handling"""
        try:
            self.options.clear()
            for i, (key, item) in enumerate(self.selection.items()):
                value = getattr(item, self.key_attr)
                self.options[value] = key
                if i == 0:  # Set initial selection
                    self.value = value
                    self.item = item

            if self.radio:
                self.radio.clear()
                self.radio.options = list(self.options.keys())
                self.radio.update()

        except AttributeError as e:
            ui.notify(f"Error updating options: {str(e)}", type="negative")

    def _handle_change(self, event) -> None:
        """Handle radio selection changes with validation"""
        try:
            self.value = event.value
            key = self.options.get(self.value)
            if key is not None:
                self.item = self.selection[key]
                if self.on_change:
                    self.on_change(self.item)
        except KeyError as e:
            ui.notify(f"Invalid selection: {str(e)}", type="negative")


class MBusViewer(MBusParser):
    """Enhanced M-Bus message viewer with improved error handling and UI organization"""

    def __init__(self, solution=None):
        super().__init__()
        self.solution = solution
        self.config = MBusConfig.get()

        # Initialize UI components
        self.hex_input: Optional[ui.textarea] = None
        self.json_view: Optional[ui.code] = None
        self.details_view: Optional[ui.html] = None
        self.error_view: Optional[ui.html] = None

    def create_textarea(
        self, label: str, placeholder: Optional[str] = None, height: str = "h-32"
    ) -> ui.textarea:
        """Create a consistent textarea with error handling"""
        return (
            ui.textarea(label=label, placeholder=placeholder)
            .classes(f"w-full {height}")
            .props("clearable outlined")
        )

    def setup_ui(self) -> None:
        """Create the main UI layout with two-column design"""
        try:
            ui.label("M-Bus Message Parser").classes("text-2xl font-bold mb-4")

            with ui.row().classes("w-full gap-4"):
                # Left column
                with ui.column().classes("flex-1"):
                    with ui.card().classes("w-full"):
                        with ui.row().classes("gap-8"):
                            self.manufacturer_select = RadioSelection[Manufacturer](
                                "Manufacturer",
                                "name",
                                selection=self.config.manufacturers,
                            ).setup(self._on_manufacturer_change)

                            self.device_select = RadioSelection[Device](
                                "Device",
                                "model",
                                selection=self.manufacturer_select.item.devices,
                            ).setup(self._on_device_change)

                        # Device details
                        with ui.card().classes("w-full"):
                            ui.label("Device Details").classes("text-lg font-bold mb-2")
                            self.details_view = ui.html()

                        with ui.row().classes("mt-4"):
                            self.message_select = RadioSelection[MBusMessage](
                                "Message",
                                "name",
                                selection=self.device_select.item.messages,
                            ).setup(self._on_message_change)

                    # Input area
                    with ui.card().classes("w-full mt-4"):
                        self.hex_input = self.create_textarea(
                            "Enter M-Bus hex message",
                            "e.g. 68 4d 4d 68 08 00 72 26 54 83 22 77...",
                        )
                        ui.button(
                            "Parse Message", on_click=self._parse_message
                        ).classes("mt-4")

                # Right column
                with ui.column().classes("flex-1"):
                    # Results area
                    with ui.row().classes("w-full"):
                        self.error_view = ui.html().classes("text-red-500")
                        self.json_view = ui.code("", language="json").classes(
                            "w-full h-96"
                        )

        except Exception as ex:
            self._handle_error("Error setting up UI", ex)

    def _on_manufacturer_change(self, manufacturer: Manufacturer) -> None:
        """Update device options when manufacturer changes"""
        try:
            self.device_select.selection = manufacturer.devices
            self.device_select._update_options()
        except Exception as ex:
            self._handle_error("Error updating devices", ex)

    def _on_device_change(self, device: Device) -> None:
        """Update message options when device changes"""
        try:
            self.message_select.selection = device.messages
            self.message_select._update_options()
            self.details_view.content = device.as_html()
        except Exception as ex:
            self._handle_error("Error updating messages", ex)

    def _on_message_change(self, message: MBusMessage) -> None:
        """Update display when message changes"""
        try:
            self.hex_input.value = message.hex
            self.details_view.content = message.device.as_html()
            self._parse_message()
        except Exception as ex:
            self._handle_error("Error updating message display", ex)

    def _parse_message(self) -> None:
        """Parse the M-Bus message with comprehensive error handling"""
        try:
            self.json_view.content = ""
            self.error_view.content = ""

            hex_str = self.hex_input.value
            if not hex_str:
                raise ValueError("Please enter a hex message")

            error_msg, frame = self.parse_mbus_frame(hex_str)
            if error_msg:
                raise ValueError(error_msg)

            json_str = self.get_frame_json(frame)
            self.json_view.content = json_str

        except Exception as ex:
            self._handle_error("Error parsing message", ex)

    def _handle_error(self, context: str, error: Exception) -> None:
        """Centralized error handling with user feedback"""
        error_msg = f"{context}: {str(error)}"
        self.error_view.content = f"<div class='text-red-500'>{error_msg}</div>"
        ui.notify(error_msg, type="negative")

        if self.solution:
            self.solution.handle_exception(error)
