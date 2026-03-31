#!/usr/bin/python3

# SPDX-FileCopyrightText: Copyright 2025-2026 The Secureblue Authors
#
# SPDX-License-Identifier: Apache-2.0

"""
The sandboxed sound toggle function
"""

import os
import sys
import subprocess
from typing import Final

SND_MOD_FILE: Final[str] = "/etc/modprobe.d/99-sound.conf"
SND_MOD_TEXT: Final[str] = """"""


def main() -> int:
    """Set or remove the sound module override"""
    required_args_count = 2
    if len(sys.argv) != required_args_count:
        return 1

    uname = subprocess.run(["uname", "-r"], check=True, text=True, capture_output=True)
    kernel = uname.stdout.strip()
    find = subprocess.Popen(
        ["find", f"/lib/modules/{kernel}/kernel/sound", "-type", "f", "-name", "*.ko.xz"],
        stdout=subprocess.PIPE,
        text=True,
    )
    sed = subprocess.Popen(
        ["sed", "s/.*\\//install /; s/\\.ko\\.xz/ \\/bin\\/false/"],
        stdin=find.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )

    find.stdout.close()

    out = sed.communicate()

    SND_MOD_TEXT = out[0]

    mode = sys.argv[1]
    match mode:
        case "on":
            with open(SND_MOD_FILE, "w", encoding="utf8") as fd:
                fd.write(SND_MOD_TEXT)
            os.chmod(SND_MOD_FILE, 0o644)
            print("Sound has been enabled. Reboot for effect.")
            return 0
        case "off":
            os.remove(SND_MOD_FILE)
            print("Sound has been disabled. Reboot for effect.")
            return 0
        case _:
            print("Invalid inner script argument.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
