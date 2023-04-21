import paramiko
import os
from jira import JIRA


class Ibox:
    def __init__(self, serial_number: int, username: str, jira: JIRA) -> None:
        self.serial_number = serial_number
        self.username = username
        self.jira = jira

    def get_serial(self) -> int:
        return self.serial_number

    def connect_to_sa(self) -> paramiko.SSHClient:
        return self._connect_to_server("m-ibox" + str(self.serial_number))

    def connect_to_node(self, node_number: int) -> paramiko.SSHClient:
        return self._connect_to_server("ibox" + str(self.serial_number) + "-{}".format(str(node_number)))

    def _connect_to_server(self, hostname: str) -> paramiko.SSHClient:
        try:
            key = paramiko.rsakey.RSAKey.from_private_key_file("/home/jenkins/.ssh/mfg_root_id")
        except FileNotFoundError:
            key = paramiko.rsakey.RSAKey.from_private_key_file("/Users/{}/.ssh/mfg_root_id".format(self.username))
        # key = paramiko.rsakey.RSAKey.from_private_key_file("/home/jenkins/.ssh/mfg_root_id")
        # key = paramiko.rsakey.RSAKey.from_private_key_file("/Users/mentelis/.ssh/mfg_root_id")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, 22, "root", pkey=key, timeout=5)
        return ssh
