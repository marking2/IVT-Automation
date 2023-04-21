from .component import Component
from paramiko import SSHClient


class UtilityDrawer(Component):
    def __init__(self, connection: SSHClient, part_name: int):
        self.serial = self._get_serial()
        super(UtilityDrawer, self).__init__(connection, part_name)

    def get_name(self) -> str:
        return "1U"

    def _get_serial(self) -> str:
        return "No S/N"

    def get_model_parent(self) -> str:
        return "Utility Drawer (1U)"

    def _get_model(self) -> str:
        return "ATS-00002-0 - Utility Drawer WTI ATS"

    def get_rc_parent(self) -> str:
        return "Other (Add in Comment)"

    def get_summary(self) -> str:
        return "1U replacement"

    def get_original_location(self) -> str:
        return "1U"
