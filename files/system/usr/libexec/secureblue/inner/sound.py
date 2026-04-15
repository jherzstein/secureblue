#!/usr/bin/python3

# SPDX-FileCopyrightText: Copyright 2025-2026 The Secureblue Authors
#
# SPDX-License-Identifier: Apache-2.0

"""
The sandboxed sound toggle function
"""

import os
import sys
from typing import Final

SND_MOD_FILE: Final[str] = "/etc/modprobe.d/99-sound.conf"
SND_MOD_TEXT: Final[str] = """"""


def main() -> int:
    """Set or remove the sound module override"""
    required_args_count = 2
    if len(sys.argv) != required_args_count:
        return 1


    mode = sys.argv[1]
    match mode:
        case "on":
            os.remove(SND_MOD_FILE)
            print("Sound has been enabled. Reboot for effect.")
            return 0
        case "off":
            kernel = os.uname().release
            root_dir = f"/lib/modules/{kernel}/kernel/sound"
            unwanted_modules = []

            for dirpath, dirnames, filenames in os.walk(root_dir):
                for f in filenames:
                    if f.endswith(".ko.xz"):
                        unwanted_modules.append(os.path.basename(f).split('.',1)[0])

            for module in unwanted_modules:
                module = module.replace("-", "_")
                SND_MOD_TEXT += f"install {module} /bin/false\n"

            with open(SND_MOD_FILE, "w", encoding="utf8") as fd:
                fd.write(SND_MOD_TEXT)
            os.chmod(SND_MOD_FILE, 0o644)
            print("Sound has been disabled. Reboot for effect.")
            return 0
        case _:
            print("Invalid inner script argument.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
