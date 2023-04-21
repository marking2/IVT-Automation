import sys
from socket import *
from paramiko import SSHClient

from .component import Component


class UPS(Component):
    MODELS = ["BBU-00006 - UPS,APC,SMT1500RMI1U,1500VA,RM,1U,230V,Production,A1,BATTERY BACKUP UNIT",
              "BBU-00001-A - UPS,EATON,5P 1550IR,208-220V,1500KVA + NMC"]

    def __init__(self, connection: SSHClient, part_name: int, ibox):
        super(UPS, self).__init__(connection, part_name)
        self.ibox = ibox

    def get_name(self) -> str:
        return "ups"

    def _get_serial(self) -> str:
        try:
            _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
        except socket.timeout as s:
            print("Can't run snmp on Node-1, attempting to connect to SA \n", s)
            try:
                self.connection = self.ibox.connect_to_sa()
                _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
            except socket.timeout as s:
                print("Can't run snmp on SA, attempting to connect to Node-2 \n", s)
                try:
                    self.connection = self.ibox.connect_to_node(2)
                    _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
                except socket.timeout as s:
                    print("Can't run snmp on Node-2, attempting to connect to Node-3 \n", s)
                    try:
                        self.connection = self.ibox.connect_to_node(3)
                        _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
                    except socket.timeout as s:
                        print("Can't run snmp on any of the nodes, check connection", s)
                        sys.exit(1)
        lines = stdout.readlines()
        for line in lines:
            if line.__contains__("ups.serial"):
                return line.split()[-1]

    def get_model_parent(self) -> str:
        return "BBU"

    def _get_model(self) -> str:
        return self.MODELS[0]

    def _get_commands(self) -> [str]:
        return ["ups-client.py"]

    def get_rc_parent(self) -> str:
        return "BBU"

    def get_summary(self) -> str:
        return "BBU-{} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "BBU-{}".format(self.part_name)
