from .component import Component
from paramiko import SSHClient


class Enclosure(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        super(Enclosure, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "enclosures"

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        for line in lines:
            if len(line.split()) > 1:
                if line.split()[1] == str(self.part_name):
                    return line.split()[-1]

    def get_model_parent(self) -> str:
        return "Enclosure"

    def _get_model(self) -> str:
        return "ENC-00001-A-CS - ENCL,SANMINA,NDS4600,05.09.05,4U,60XHDD"

    def _get_commands(self) -> [str]:
        return ["DV_LOC=1 /mnt/logs/runx_ivtdash/rund_latest 0 247"]

    def get_rc_parent(self) -> str:
        return "Enclosures - Sanmina"

    def get_summary(self) -> str:
        return "Enclosure-{} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "Enclosure-{}".format(self.part_name)
