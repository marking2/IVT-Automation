from paramiko import SSHClient
from .component import Component


class Node(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        super(Node, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "node"

    def _get_serial(self) -> str:
        stdin, stdout, stderr = self.connection.exec_command(self._get_commands()[1])
        line = stdout.readlines()
        return line

    def get_model_parent(self) -> str:
        return "Node"

    def _get_commands(self) -> [str]:
        return ["racadm getsysinfo",
                "racadm getsvctag"]

    def get_rc_parent(self) -> str:
        return "Node"

    def get_summary(self) -> str:
        return "node-{} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "node-{}".format(self.part_name)

    def get_node_number(self) -> str:
        return "{}".format(self.part_name)