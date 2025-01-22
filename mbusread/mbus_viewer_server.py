"""
Created on 22.01.2025

@author: wf
"""

import os

from ngwidgets.input_webserver import InputWebserver, InputWebSolution, WebserverConfig
from nicegui import Client

from mbusread.mbus_config import MBusExamples
from mbusread.mbus_viewer import  MBusViewer
from mbusread.version import Version


class NiceMBusWebserver(InputWebserver):
    """
    webserver to demonstrate ngwidgets capabilities
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2025 Wolfgang Fahl"
        config = WebserverConfig(
            short_name="mbus_viewer",
            timeout=6.0,
            copy_right=copy_right,
            version=Version(),
            default_port=9853,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = NiceMBus
        return server_config

    def __init__(self):
        """
        Constructor
        """
        InputWebserver.__init__(self, config=NiceMBusWebserver.get_config())
        pass

    def configure_run(self):
        root_path = (
            self.args.root_path if self.args.root_path else MBusExamples.examples_path()
        )
        self.root_path = os.path.abspath(root_path)
        self.allowed_urls = [
            "https://raw.githubusercontent.com/WolfgangFahl/nicescad/main/examples/",
            "https://raw.githubusercontent.com/openscad/openscad/master/examples/",
            self.root_path,
        ]


class NiceMBus(InputWebSolution):
    """ """

    def __init__(self, webserver: "NiceMBusWebserver", client: Client):
        super().__init__(webserver, client)

    async def home(self):
        """
        provide the main content page
        """

        def setup_home():
            viewer = MBusViewer(solution=self)
            viewer.setup_ui()

        await self.setup_content_div(setup_home)
