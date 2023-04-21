import os
import time

from .component import Component
from paramiko import SSHClient
from typing import Union
from Ibox import Ibox

REJECTION_CRITERIA = {
    "sense_02_04_02_fails_to_spin_up": "RC-EDSK01 - Drive fails to spin up",
    "Glist": "RC-EDSK02 - GLIST TH exceeded",
    "uncor_write": "RC-EDSK03 - Uncorrectable Write Errors TH exceeded",
    "Smart status not OK": "RC-EDSK04 - SMART status not OK",
    "scan_04": "RC-EDSK05 - Hardware Error: Scan 04 counter > 0",
    "sense_72_04_hardware_error": "RC-EDSK06 - Hardware Error: Sense (72) 04",
    "smart_status_5d": "RC-EDSK07 - SMART code non zero (5D xx)",
    "excessive_medium_errors": "RC-EDSK08 - Excessive Medium Errors (64 consecutive errors)",
    "missing_from_scsi": "RC-EDSK09 - Drive is missing from SCSI",
    "sense_72_03_medium_format_corrupted": "RC-EDSK10 - Medium Format Corrupted: Sense (72) 03 31",
    "Internal_target_errors": "RC-EDSK11 - Internal Target Errors > 64 (72)",
    "dwords_links_drive_side": "RC-EDSK12 - Drive bay with noisy DWORD errors - drive side",
    "slow_response": "RC-EDSK13 - Slow Response",
    "scan_03": "A high sum of uncorrectable read, verify and scan 03 errors",
    "uncor_read": "A high sum of uncorrectable read, verify and scan 03 errors",
    "uncor_verify": "A high sum of uncorrectable read, verify and scan 03 errors"
}
REPLACEMENT_OPTIONS = [
    "Glist",
    "scan_04",
    "scan_03",
    "uncor_write",
    "uncor_read",
    "uncor_verify",
    "sense_72_04_hardware_error",
    "smart_status_5d",
    "excessive_medium_errors",
    "missing_from_scsi",
    "sense_72_03_medium_format_corrupted",
    "Internal_target_errors",
    "dwords_links_drive_side",
    "slow_response",
    "Smart status not OK",
    "sense_02_04_02_fails_to_spin_up",
    "Other",
]


class Drive(Component):
    def __init__(self, connection: SSHClient, part_name: int, drive_type: str):
        self.drive_type = drive_type
        super(Drive, self).__init__(connection, part_name)

    def collect_logs(self, ibox: Ibox) -> Union[str, None]:
        if self.node:
            connect = ibox.connect_to_node(self.node)
        else:
            connect = ibox.connect_to_node(1)
        if "Enclosure Drive" in self.drive_type:
            cmd = self.commands[3]
        else:
            cmd = self.commands[2]
        cmd = cmd.format(self.get_sg_device(ibox))
        try:
            print("Collecting sg_logs.")
            _, stdout, _ = connect.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            sg_logs = "{noformat}\n"
            output = stdout.read().decode('ascii').strip("\n")
            sg_logs += output
            sg_logs += "\n{noformat}"
            print("sg_logs collected!")
        except Exception as e:
            print(str(e) + ' ' + str(exit_status))
        try:
            if "Enclosure Drive" in self.drive_type:
                cmd = self.commands[2]
            else:
                cmd = self.commands[1]
            cmd = cmd.format(self.get_sg_device(ibox))
            print("Collecting smartctl.")
            _, stdout, _ = connect.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('ascii').strip("\n")
            smartctl = "{noformat}\n"
            smartctl += output
            smartctl += "\n{noformat}"
            print("smartctl collected!")
        except Exception as e:
            print(str(e) + ' ' + str(exit_status))
        return sg_logs + "\n" + smartctl

    def get_name(self) -> str:  # for logs use
        return "drive"

    def _get_serial(self) -> str:
        return ""

    def get_model_parent(self) -> str:
        return ""

    def _get_model(self) -> str:
        return ""

    def _get_commands(self) -> [str]:
        return ""

    def get_sg_device(self) -> str:
        return ""

    def get_rc_parent(self) -> str:
        return ""

    def get_summary(self) -> str:
        return ""

    def get_original_location(self) -> str:
        return ""

    def set_rejection_criteria(self):
        for name, description in self.REJECTION_CRITERIA.items():
            for label in self.labels:
                if label in name:
                    return description
        return None


class EnclosureDrive(Drive):
    def __init__(self, connection: SSHClient, part_name: int, type: str):
        super(EnclosureDrive, self).__init__(connection, part_name, type)

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            drive = line.split(" ")[1]
            if drive == str(self.part_name):
                serial = []
                line = line.split(" ")
                for word in line:
                    if word:
                        serial.append(word)
                if serial:
                    return serial[4]
        return ""

    def _get_model(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[0].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            drive = line.split(" ")[1]
            if drive == str(self.part_name):
                model = []
                line = line.split(" ")
                for word in line:
                    if word:
                        model.append(word)
                if model:
                    return model[3]
        # if not found, get neighbour drive model
        for line in lines:
            for neighbour in self.get_neighbour_drive_name():
                if line.split(" ")[0] == str(neighbour):
                    model = []
                    line = line.split(" ")
                    for word in line:
                        if word:
                            model.append(word)
                    if model:
                        return model[3]
        return ""

    def get_neighbour_drive_name(self) -> [int]:
        return [self.part_name + 1, self.part_name - 1]

    def get_sg_device(self, ibox: Ibox) -> str:
        connect = ibox.connect_to_node(1)
        cmd = self._get_commands()[0].format(self.part_name)
        sg = ""
        try:
            _, stdout, _ = connect.exec_command(cmd)
            lines = stdout.readlines()
            for line in lines:
                drive = line.split(" ")[1]
                if drive == str(self.part_name):
                    sg = []
                    line = line.split(" ")
                    for word in line:
                        if word:
                            sg.append(word)
                    if sg:
                        return sg[1].split('/')[-1]
        except ValueError:
            print("Couldn't find the wanted drive: ".format("{}".format(self.part_name)))
            exit
        return sg

    def _get_commands(self) -> [str]:
        return ["DV_LOC=1 /mnt/logs/runx_ivtdash/rund_latest 0 e0 | grep {}",
                "DV_LOC=1 /mnt/logs/runx_ivtdash/rund_latest 0 2e3 | grep {}",
                "smartctl -x /dev/{}",
                "sg_logs -a /dev/{}"]

    def get_model_parent(self) -> str:
        return "Enclosure Drive"

    def get_rc_parent(self) -> str:
        return "Enclosure Drives"

    def get_rc(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[1].format(self.part_name))
        dicts = []
        for line in stdout:
            rc_dict = {}
            vals = line.split()
            rc_dict["drive"] = vals[0]
            rc_dict["glist"] = vals[12]
            rc_dict["scan_03"] = vals[18]
            rc_dict["scan_04"] = vals[19]
            dicts.append(rc_dict)

    def get_summary(self) -> str:
        return "Enclosure Drive {} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "Enclosure Drive {}".format(self.part_name)


class LocalDrive(Drive):  # MT issue!!!
    def __init__(self, connection: SSHClient, part_name: int, type: str, node_number: int, ):
        self.node = node_number
        self.part_name = self.build_part_name(part_name)
        super(LocalDrive, self).__init__(connection, self.part_name, type)

    def build_part_name(self, part_name) -> str:
        if part_name < 10:
            return "N{}D0{}".format(self.node, part_name)
        return "N{}D{}".format(self.node, part_name)

    def get_neighbour_drive_name(self) -> str:
        drive_number = int(self.part_name.split("D")[-1])
        if drive_number == 1:
            return "N{}D0{}".format(self.node, str(drive_number + 1))
        else:
            return "N{}D0{}".format(self.node, str(drive_number - 1))

    def get_model_parent(self) -> str:
        return "Local Drive"

    def _get_commands(self) -> [str]:
        return ["ldm-cli.py",
                "smartctl -x /dev/{}",
                "sg_logs -a /dev/{}",
                "ldm-cli.py -T | grep {}",
                "HBA=0 rund 0 2e3"]

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[3].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            if line.split(" ")[0] == self.part_name:
                serial = []
                line = line.split(" ")
                for word in line:
                    if word:
                        serial.append(word)
                if serial:
                    return serial[5]
        return ""

    def _get_model(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[3].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            if line.split(" ")[0] == self.part_name:
                model = []
                line = line.split(" ")
                for word in line:
                    if word:
                        model.append(word)
                if model:
                    return model[3]
        # if not found, get neighbour drive model
        for line in lines:
            if line.split(" ")[0] == self.get_neighbour_drive_name():
                model = []
                line = line.split(" ")
                for word in line:
                    if word:
                        model.append(word)
                if model:
                    return model[3]
        return ""

    def get_sg_device(self, ibox: Ibox) -> str:
        connect = ibox.connect_to_node(self.node)
        cmd = self._get_commands()[0].format(self.part_name)
        sg = ""
        try:
            _, stdout, _ = connect.exec_command(cmd)
            lines = stdout.readlines()
            for line in lines:
                drive = line.split(" ")[0]
                if drive == str(self.part_name):
                    sg = []
                    line = line.split(" ")
                    for word in line:
                        if word:
                            sg.append(word)
                    if sg:
                        return sg[7].split('/')[-1]
        except ValueError:
            print("Couldn't find the wanted drive: ".format("{}".format(self.part_name)))
            exit
        return sg

    def get_rc_parent(self) -> str:
        return "Local Disk"

    def get_summary(self) -> str:
        return "Local Drive {} replacement".format(self.part_name)

    def get_node_number(self) -> str:
        return "{}".format(self.node)


class SSD(Drive):
    def __init__(self, connection: SSHClient, part_name: int, type: str, node_number: int):
        self.node = node_number
        self.part_name = self.build_part_name(part_name)
        super(SSD, self).__init__(connection, self.part_name, type)

    def build_part_name(self, part_name) -> str:
        if part_name < 10:
            return "N{}D0{}".format(self.node, part_name)
        return "N{}D{}".format(self.node, part_name)

    def get_neighbour_drive_name(self) -> str:
        drive_number = int(self.part_name.split("D")[-1])
        if drive_number == 9 or 10:
            return "N{}D{}".format(self.node, str(drive_number + 1))
        else:
            return "N{}D{}".format(self.node, str(drive_number - 1))

    def get_model_parent(self) -> str:
        return "Local Drive"

    def _get_commands(self) -> [str]:
        return ["ldm-cli.py",
                "smartctl -x /dev/{}",
                "sg_logs -a /dev/{}",
                "ldm-cli.py -T"]

    def _get_serial(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[3].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            if line.split(" ")[0] == self.part_name:
                serial = []
                line = line.split(" ")
                for word in line:
                    if word:
                        serial.append(word)
                if serial:
                    return serial[5]
        return ""

    def _get_model(self) -> str:
        _, stdout, _ = self.connection.exec_command(self._get_commands()[3].format(self.part_name))
        lines = stdout.readlines()
        for line in lines:
            if line.split(" ")[0] == self.part_name:
                model = []
                line = line.split(" ")
                for word in line:
                    if word:
                        model.append(word)
                if model and "-" not in model:
                    if ("_" or "/") in model[3]:
                        model = model[3].split("_")[-1]
                        return model
        # if not found, get neighbour drive model
        for line in lines:
            if line.split(" ")[0] == self.get_neighbour_drive_name():
                model = []
                line = line.split(" ")
                for word in line:
                    if word:
                        model.append(word)
                if model:
                    if ("_" or "/") in model[3]:
                        model = model[3].split("_")[-1]
                        return model
        return ""

    def get_sg_device(self, ibox: Ibox) -> str:
        connect = ibox.connect_to_node(self.node)
        cmd = self._get_commands()[0].format(self.part_name)
        sg = ""
        try:
            _, stdout, _ = connect.exec_command(cmd)
            lines = stdout.readlines()
            for line in lines:
                drive = line.split(" ")[0]
                if drive == str(self.part_name):
                    sg = []
                    line = line.split(" ")
                    for word in line:
                        if word:
                            sg.append(word)
                    if sg:
                        return sg[7].split('/')[-1]
        except ValueError:
            print("Couldn't find the wanted drive: ".format("{}".format(self.part_name)))
            exit
        return sg

    def get_rc_parent(self) -> str:
        return "Local Disk"

    def get_summary(self) -> str:
        return "SSD {} replacement".format(self.part_name)

    def get_original_location(self) -> str:
        return "{} SSD".format(self.part_name)

    def get_node_number(self) -> str:
        return "{}".format(self.node)
