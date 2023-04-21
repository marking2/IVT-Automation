from .enclosure import Enclosure
from paramiko import SSHClient


class PCM(Enclosure):
    def __init__(self, connection: SSHClient, part_name: int, side: str):
        self.side = side.upper()
        super(PCM, self).__init__(connection, part_name)

    # get_name() is the same as enclosure

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0])
        lines = stdout.readlines()
        if len(lines) == 0:
            print("rund_latest is not available, trying an older version of rund")
            _, stdout, _ = self.connection.exec_command(self._get_commands()[2])
            lines = stdout.readlines()
        for line in lines:
            if line.__contains__("NEWISYS"):
                if line.split()[9] == str(self.part_name):
                    sg_device = line.split()[2].split("/")[-1]

                    cmd = self._get_commands()[1].format(sg_device)
                    stdin, stdout, stderr = self.connection.exec_command(cmd)
                    lines = stdout.readlines()
                    for line in lines:
                        if line.split().__contains__("PCM") and line.split().__contains__(self.side.upper()):
                            return line.split()[-1]

    def get_model_parent(self) -> str:
        return "PSU"

    def _get_model(self) -> str:
        return "PSU-00001-A - PSU,SANMINA,PWR-00059-01-B,1200W"

    def _get_commands(self) -> [str]:
        return ["DV_LOC=1 /mnt/logs/runx_ivtdash/rund_latest 0 1e0",
                "sg_ses -p 0x7 /dev/{} | grep -A 5 Temperature | grep -i pcm",
                "rund 0 1e0"]

    def get_rc_parent(self) -> str:
        return "Sanmina PSU"

    def get_summary(self) -> str:
        return "Enclosure-{} PCM-{} replacement".format(self.part_name, self.side)

    def get_original_location(self) -> str:
        return "Enclosure-{} PCM-{}".format(self.part_name, self.side)
