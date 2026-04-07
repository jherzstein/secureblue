#!/usr/bin/python3

# SPDX-FileCopyrightText: Copyright 2025-2026 The Secureblue Authors
#
# SPDX-License-Identifier: Apache-2.0

"""
The sound toggle implementation for ujust
"""

import sys
from pathlib import Path
from typing import Final

import subprocess
import sandbox
from utils import (
    ask_yes_no,
    is_module_loaded,
    loaded_kernel_modules,
)

SND_HELP: Final[str] = """
This python script toggles if sound is enabled by creating or deleting a modprobe file at
"/etc/modprobe.d/99-sound.conf" to disable or enable the kernel modules
needed for Sound. Note this change only takes affect upon reboot.

usage:
ujust set-sound-modules
    Turns Sound on or off interactively based on the user's preference.

ujust set-sound-modules on
    Turns Sound on, does nothing if already on.

ujust set-sound-modules off
    Turns Sound off, does nothing if already off.

ujust set-sound-modules status
    Reports if Sound is set on or off.

ujust set-sound-modules --help
    Prints this message.
"""

SND_MOD_DIR: Final[str] = "/etc/modprobe.d"
SND_MOD_FILE: Final[str] = f"{SND_MOD_DIR}/99-sound.conf"


def print_status(disabled_by_file: bool) -> None:
    """Print the current file and runtime status"""
    blocked_modules = []

    uname = subprocess.run(["uname", "-r"], capture_output=True, check=True, text=True)
    kernel = uname.stdout.strip()
    find = subprocess.Popen(
        ["find", f"/lib/modules/{kernel}/kernel/sound", "-type", "f", "-name", "*.ko.xz"],
        stdout=subprocess.PIPE,
        text=True,
    )
    sed = subprocess.Popen(
        ["sed", "s/.*\\///; s/\\.ko\\.xz//; s/-/_/g"],
        stdin=find.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )
    find.stdout.close()
    out = sed.communicate()

    blocked_modules = out[0].splitlines()
    unwanted_modules = []
    loaded_modules = loaded_kernel_modules()
    unwanted_modules = [mod for mod in blocked_modules if mod in loaded_modules]
    sound_currently_enabled = [len(unwanted_modules) > 0]
    file_matches_sys = "still " if disabled_by_file != sound_currently_enabled else ""
    cur_status = "enabled" if sound_currently_enabled else "disabled"
    file_status = "disabled" if disabled_by_file else "enabled"

    print(
        f"Sound is currently {cur_status}, and after a reboot will",
        f"{file_matches_sys}be {file_status}",
    )


def main() -> int:
    """Handle the arguments and execute the sound toggle"""

    argc_interactive = 1
    argc_on_off = 2

    if len(sys.argv) == argc_interactive:
        # Ask interactively.
        mode = "on" if ask_yes_no("Would you like to load the Sound modules?") else "off"
    elif len(sys.argv) == argc_on_off:
        # Take mode from first argument, i.e. 'on' or 'off'.
        mode = sys.argv[1].casefold()
    else:
        print("Too many options specified, see usage with --help.", file=sys.stderr)
        return 1

    disabled_by_file = Path(SND_MOD_FILE).exists()
    sound_function = sandbox.SandboxedFunction("sound.py", read_write_paths=[SND_MOD_DIR, "/proc"])
    match mode:
        case "on" | "off":
            target_state_enabled = mode == "on"
            state_already_set = target_state_enabled != disabled_by_file
            if state_already_set:
                print_status(disabled_by_file)
            else:
                return sandbox.run(sound_function, mode)
        case "status":
            print_status(disabled_by_file)
        case "--help":
            print(SND_HELP)
        case _:
            print("Invalid option selected. Try --help.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
