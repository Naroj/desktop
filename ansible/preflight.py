"""
Python virtual env setup
Ansible will take care of the rest
"""

import os
import venv
import subprocess
import shutil
from venv import EnvBuilder as builder

INCL_SYSTEM = True
WIPE = False
INCL_PIP = True
HOME = os.getenv("HOME")
DST = f"{HOME}/.venv"
SHELL = os.getenv("SHELL")
BASE_PACKAGES = ["ansible"]

def create_venv() -> None:
    print(f"creating venv: {DST}")
    my_venv = builder(system_site_packages=INCL_SYSTEM,clear=WIPE,with_pip=INCL_PIP)
    my_venv.ensure_directories(DST)
    try:
        my_venv.create(DST)
    except shutil.SameFileError:
        print("venv already exists")
        pass

def install_base() -> None:
    print(f"install base packages {BASE_PACKAGES}")
    cmd = [f"{DST}/bin/pip", "install"]
    subprocess.run([*cmd, *BASE_PACKAGES], capture_output=True)

def add_bin_to_shell() -> None:
    path_line, conf, content = None, None, None
    if "bash" in SHELL:
        conf = f"{HOME}/.bashrc"
        path_line = f"PATH=$PATH:{DST}/bin"
        with open(conf, "r") as fp:
            content = fp.read()
    else:
        print("can't add venv bin to path, your shell is not supported")
        return
    if conf and path_line not in content:
        print(f"adding virtual env bin to PATH, reload {conf} to activate right now")
        with open(conf, "a") as fp:
            fp.write(f"{path_line}\n")



if __name__ == "__main__":
    create_venv()
    install_base()
    add_bin_to_shell()
