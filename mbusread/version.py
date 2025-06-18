"""
Created on 22.01.2025

@author: wf
"""

from dataclasses import dataclass

import mbusread


@dataclass
class Version:
    """
    Version handling for nicegui widgets
    """

    name = "mbusreader"
    version = mbusread.__version__
    date = "2025-01-22"
    updated = "2025-06-18"
    description = "MBus message parser and JSON result viewer"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/MBus_Reader"
    chat_url = "https://github.com/WolfgangFahl/mbusreader/discussions"
    cm_url = "https://github.com/WolfgangFahl/mbusreader"

    license = f"""Copyright 2025 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
