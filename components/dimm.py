from paramiko import SSHClient
from .component import Component
from .node import Node


class DIMM(Node):
    def __init__(self, connection: SSHClient, part_name: int, part_location: str, node_number: int):
        self.locator = part_location + str(part_name)
        self.node_tag = self.get_node_serial()
        self.node = node_number
        super(DIMM, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "dimm"

    def _get_serial(self) -> str:
        stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        serial = ""
        found = False
        for line in lines:
            if "Locator" in line:
                locator = line.split()[-1]
                if locator == self.locator:
                    found = True
            if "Serial Number" in line and found:
                serial = line.split()[-1]
        return serial

    def get_node_serial(self) -> str:
        return super()._get_serial()

    def get_model_parent(self) -> str:
        return "DIMM"

    def _get_model(self) -> str:
        stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        model = ""
        found = False
        for line in lines:
            if "Locator" in line:
                locator = line.split()[-1]
                if locator == self.locator:
                    found = True
            if "Part Number" in line and found:
                model = line.split(" ")[-1]
        return model

    def _get_commands(self) -> [str]:
        return ["dmidecode --type 17", ]

    def get_rc_parent(self) -> str:
        return "DIMM/SFP/Fan"

    def get_summary(self) -> str:
        return "Node-{} DIMM-{}{} replacement".format(self.node, self.locator, self.part_name)

    def get_original_location(self) -> str:
        return "Node-{} DIMM-{}{}".format(self.node, self.locator, self.part_name)

    def get_node_number(self) -> str:
        return "{}".format(self.node)