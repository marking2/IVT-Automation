from .component import Component
from paramiko import SSHClient


class ATS(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        self.serial = self._get_serial()
        super(ATS, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "ats"

    def _get_serial(self) -> str:
        return "No S/N"

    def get_model_parent(self) -> str:
        return "Utility Drawer (1U)"

    def _get_model(self) -> str:
        return "ATS-00107-A - ATS,ASSY,PCB,OMRON,NEW ATS-V7"

    def get_rc_parent(self) -> str:
        return "ATS"

    def get_summary(self) -> str:
        return f"ATS-{self.part_name} replacement"

    def get_original_location(self) -> str:
        return f"ATS-{self.part_name}"
