from paramiko import SSHClient
import sys

from .component import Component


class Infiniband(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        self.part_address = self._get_part_address()
        super(Infiniband, self).__init__(connection, part_name)

    def get_name(self) -> str:  # no logs collection needed
        return ""

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self.get_commands()[1])
        lines = stdout.readlines()
        for line in lines:
            if "Serial number" in line:
                serial = line.split()[-1]
        return serial

    def _get_model(self) -> str:
        return "PCI-00003-A - PCI,HBA,MELLANOX,MCX353A-FCBT,2 PORTS,56GBPS+FW"

    def get_model_parent(self) -> str:
        return "Node Components"

    def _get_commands(self) -> [str]:
        return ["lspci| grep -i mellanox",
                f"lspci -vv -s {self.part_address}"]

    def _get_part_address(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        if self.part_name == 1:
            address = lines[0].split(" ")[0]
        else:
            address = lines[0].split(" ")[1]
        return address

    def get_rc_parent(self) -> str:
        return ""

    def get_summary(self) -> str:
        return f"IB Card-{self.part_name} replacement"

    def get_original_location(self) -> str:
        return f"Mellanox-{self.part_name} card"
