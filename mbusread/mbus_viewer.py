"""
Created on 2025-01-22

@author: wf
"""

from nicegui import ui

from mbusread.mbus_parser import MBusParser


class MBusViewer(MBusParser):
    """
    Meterbus message viewer with JSON editor support
    """

    def __init__(self, solution=None):
        super().__init__()
        self.solution = solution
        self.hex_input = None
        self.json_code = None
        self.example_select = None
        self.error_html = None

    def createTextArea(self, label, placeholder=None, classes: str = "h-64"):
        """Create a standardized textarea with common styling"""
        textarea = (
            ui.textarea(label=label, placeholder=placeholder)
            .classes("w-full")
            .props(f"input-class={classes}")
            .props("clearable")
        )
        return textarea

    def on_parse(self):
        """Handle parse button click"""
        try:
            with self.result_row:
                self.json_code.content = ""
                self.error_view.content = ""
                mbus_hex_str = self.hex_input.value
                error_msg, frame = self.parse_mbus_frame(mbus_hex_str)
                if error_msg:
                    self.error_view.content = f"{error_msg}"
                else:
                    json_str = self.get_frame_json(frame)
                    self.json_code.content = json_str
        except Exception as ex:
            self.solution.handle_exception(ex)

    def on_example_change(self):
        """Handle example selection change"""

        selected = self.example_select.value
        if selected in self.examples:
            example = self.examples[selected]
            self.hex_input.value = example.hex
            self.example_details.content = example.as_html()
            self.on_parse()

    def setup_ui(self):
        """Create the NiceGUI user interface"""
        try:
            ui.label("M-Bus Message Parser").classes("text-h4 q-mb-md")

            self.example_select = ui.select(
                label="Select Example",
                options=list(self.examples.keys()),
                on_change=self.on_example_change,
            ).classes("w-full q-mb-md")

            self.example_details = ui.html().classes("w-full mb-4")

            self.hex_input = self.createTextArea(
                label="Enter M-Bus hex message",
                placeholder="e.g. 68 4d 4d 68 08 00 72 26 54 83 22 77...",
                classes="h-32",
            )

            with ui.row() as self.button_row:
                ui.button("Parse Message", on_click=self.on_parse).classes("q-mt-md")
            with ui.row() as self.result_row:
                self.error_view = ui.html()
                self.json_code = ui.code(content="",language="json").classes("w-full h-96 q-mt-md")
        except Exception as ex:
            self.solution.handle_exception(ex)