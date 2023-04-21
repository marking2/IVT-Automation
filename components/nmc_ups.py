from paramiko import SSHClient
import socket
import sys

from .ups import UPS


class UpsNmc(UPS):
    MODELS = {
        "AP9630": "CRD-00011 - CARD,NMC,APC,AP9630,Production,A",
        "AP9640": "CRD-00028 - CARD,NMC,APC,AP9640"
    }

    def __init__(self, connection: SSHClient, part_name: int, ibox):
        super(UpsNmc, self).__init__(connection, part_name)
        self.ibox = ibox

    def get_name(self) -> str:  # no nmc logs collection needed
        return ""

    def _get_serial(self) -> str:
        try:
            _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
        except socket.timeout as s:
            print("Can't run snmp on Node-1, attempting to connect to Node-2 \n", s)
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

        line = stdout.readline()
        values = line.split()
        if "SN:" in values:
            return values[values.index("SN:") + 1]

    def _get_model(self) -> str:
        try:
            _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
        except socket.timeout as s:
            print("Can't run snmp on Node-1, attempting to connect to Node-2 \n", s)
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
        line = stdout.readline()
        values = line.split()
        model = ""
        for value in values:
            if "MN:" in value:
                model = value.split(":")[-1]
        for key, value in self.MODELS.items():
            if model == key:
                return value

    def _get_commands(self) -> [str]:
        return ["snmpget -v1 -c public ups-{} .1.3.6.1.2.1.1.1.0"]

    def get_rc_parent(self) -> str:
        return "BBU"

    def get_summary(self) -> str:
        return "BBU-{} NMC replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "BBU-{} NMC".format(self.part_name)
