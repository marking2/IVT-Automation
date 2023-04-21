from .component import Component
from paramiko import SSHClient


class Switch(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        super(Switch, self).__init__(connection, part_name)
        self.serial = self._get_serial()
        self.model = self._get_model()

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        serial = ""
        for line in lines:
            if "serial" in line:
                serial = line.split()[-1]
        return serial

    def _get_model(self) -> str:
        return "SWI-00001-A - NETGEAR,GS116E"

    def get_model_parent(self) -> str:
        return "Internal Switch"

    def _get_commands(self) -> str:
        return "eth-switch.py"

    def get_rc_parent(self) -> str:
        return "Netgear"

    def get_summary(self) -> str:
        return "Netgear Switch replacement"

    def get_original_location(self) -> str:
        return "Netgear Switch"
