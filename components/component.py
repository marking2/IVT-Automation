from paramiko import SSHClient

from Ibox import Ibox
from typing import Union


class Component:
    def __init__(self, connection: SSHClient, part_name: int) -> None:
        self.connection = connection
        self.part_name = part_name
        self.serial = self._get_serial()
        self.model = self._get_model()
        self.commands = self._get_commands()
        self.name = self.get_name()
        self.node = self.get_node_number()

    def collect_logs(self, ibox: Ibox) -> Union[str, None]:
        connect = ibox.connect_to_sa()
        if ("sfp" or "dimm" or "node") in self.name:
            cmd = "/opt/infinidat/sa-utils/utils/log-collector.py -l dell -n {} --no-timeout <<< yes".format(self.node)
        else:
            cmd = "/opt/infinidat/sa-utils/utils/log-collector.py -l {} --nodes=1,2,3 --no-timeout <<< yes".format(
                self.name)
        print("Collecting logs, this may take a while.")
        try:
            _, stdout, _ = connect.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
        except Exception as e:
            print(str(e) + ' ' + str(exit_status))
        lines = stdout.readlines()
        for line in lines:
            print(line)
        try:
            if exit_status == 0:
                print("Logs Collected")
                logs_path = lines[-1].split()[-1]
                ftp_client = connect.open_sftp()
                ftp_client.get(logs_path, logs_path)
                ftp_client.close()
                return logs_path
        except Exception as exception:
            print(str(exception) + ' ' + str(exit_status))
            return None

    def get_name(self) -> str:  # for logs use
        return ""

    def _get_serial(self) -> str:
        return ""

    def get_model_parent(self) -> str:
        return ""

    def _get_model(self) -> str:
        return ""

    def _get_commands(self) -> [str]:
        return []

    def get_rc_parent(self) -> str:
        return ""

    def get_summary(self) -> str:
        return ""

    def get_original_location(self) -> str:
        return ""

    def get_node_number(self) -> str:
        return ""

    def __str__(self):
        str_dict = {"name": self.get_original_location(),
                    "part_number": self.part_name,
                    "serial": self.serial,
                    "model": self.model,
                    "commands": self.commands,
                    "node_number": self.node}
        final = ""
        for key, value in str_dict.items():
            final += key + ": " + str(value) + ",\n"
        return final
