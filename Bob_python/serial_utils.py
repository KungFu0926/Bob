import re

from serial.tools.list_ports_linux import comports


def getSerialNameByDescription(description: str):
    for port in comports():
        if re.search(description, port.description):
            return port.package_device
    raise Exception(description + " not found.")
