from paramiko import SSHClient
from .component import Component
from .node import Node


class SFP(Node):
    def __init__(self, connection: SSHClient, part_name: int, sfp_type: str, node_number: int):
        self.type = sfp_type
        self.node_serial = self.get_node_serial()
        self.node = node_number
        super(SFP, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "sfp"

    def _get_serial(self) -> str:
        if self.type == "FC":
            stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[0])
            lines = stdout.readlines()
            serial = ""
            for line in lines:
                if "Serial number" in line:
                    serial = line.split()[-1]
        else:
            stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[1])
            lines = stdout.readlines()
            serial = ""
            for line in lines:
                if "Vendor SN" in line:
                    serial = line.split()[-1]
        return serial

    def get_node_serial(self) -> str:
        return super()._get_serial()

    def get_model_parent(self) -> str:
        return "Node Components"

    def _get_model(self) -> str:
        if self.type == "FC":
            stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[0])
            lines = stdout.readlines()
            model = ""
            for line in lines:
                if "Vendor PN" in line:
                    model = line.split(" ")[-1]
        else:
            stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[1])
            lines = stdout.readlines()
            model = ""
            for line in lines:
                if "Vendor PN" in line:
                    model = line.split(" ")[-1]
        return model

    def _get_commands(self) -> [str]:
        return ["qladm -i {} -o sfp".format(self.part_name - 1),
                "ethtool -m eth-data{}".format(self.part_name)]

    def get_rc_parent(self) -> str:
        return "DIMM/SFP/Fan"

    def get_summary(self) -> str:
        return "Node-{} {} SFP-{} replacement".format(self.node, self.type, self.part_name)

    def get_original_location(self) -> str:
        return "Node-{} {} SFP-{}".format(self.node, self.type, self.part_name)

    def get_node_number(self) -> str:
        return "{}".format(self.node)
