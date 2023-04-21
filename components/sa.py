from .component import Component
from paramiko import SSHClient


class SA(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        super(SA, self).__init__(connection, part_name)
        self.smartctl = self.get_smart()

    def _get_serial(self) -> str:
        if self.connection:
            _, stdout, _ = self.connection.exec_command(self._get_commands()[1])
            lines = stdout.readlines()
            for line in lines:
                if "Serial Number" in line:
                    return line.split(" ")[-1]
        return None

    def get_smart(self) -> str:
        if self.connection:
            _, stdout, _ = self.connection.exec_command(self._get_commands()[0])
            lines = stdout.readlines()
            smart = "{noformat} " + "smartctl -x /dev/sda \n"
            for line in lines:
                smart += line + "\n"
            smart += "\n {noformat}"
        return ""

    def get_model_parent(self) -> str:
        return "Utility Drawer (1U)"

    def _get_model(self) -> str:
        return "SA-00001-A - SA,COMPULAB,FIT PC3"

    def _get_commands(self) -> [str]:
        return ["smartctl -x /dev/sda",
                "dmidecode | grep -i Serial"]

    def get_rc_parent(self) -> str:
        return "SA"

    def get_summary(self) -> str:
        return "SA replacement"

    def get_original_location(self) -> str:
        return "SA"
