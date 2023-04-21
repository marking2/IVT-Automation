import argparse
import logging
import socket
import sys

from paramiko.ssh_exception import NoValidConnectionsError

from components.enclosure import Enclosure
from components.iom import IOM
from components.pcm import PCM
from components.pdu import PDU
from components.ups import UPS
from components.sa import SA
from components.switch import Switch
from components.nmc_ups import UpsNmc
from components.node import Node
from components.dimm import DIMM
from components.sfp import SFP
from components.drive import EnclosureDrive
from components.drive import LocalDrive
from components.drive import SSD
from components.utility_drawer import UtilityDrawer
from components.ats import ATS


def get_user_info(user, password):
    if '@' in user:
        user = user.split('@')[0]
    if not password:
        print("No password provided")
        exit()
    return {"name": user,
            "password": password}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "ibox",
        type=int,
        help="IBOX serial number, Required"
    )
    ap.add_argument(
        "component",
        type=str,
        help="Component name: enclosure, iom, pcm, pdu, ups, sa, nmc, dimm, sfp, drive, node"
    )
    ap.add_argument(
        "part_name",
        nargs="?",
        type=int,
        help="Component's name in the ibox i.e for ups-2 : 2"
    )
    ap.add_argument(
        "-s",
        "--side",
        type=str,
        nargs="?",
        default="None",
        help="Component's side(a, b)"
    )
    ap.add_argument(
        "--no-logs",
        dest="noLogs",
        type=str,
        default="false",
        help="Don't collect logs"
    )
    ap.add_argument(
        "-u",
        "--user",
        help="JIRA user name"
    )
    ap.add_argument(
        "-p",
        "--password",
        help="JIRA user password"
    )
    ap.add_argument(
        "-f",
        "--file",
        help="mfg_root_id file for servers connection"
    )
    ap.add_argument(
        "-rc",
        "--rejection",
        type=str,
        nargs="+",
        default="None",
        help="Rejection criteria for the component"
    )
    ap.add_argument(
        "-res",
        "--resolution",
        type=str,
        default="None",
        help="Resolution: RMA, Internal Use, FA"
    )
    ap.add_argument(
        "-d",
        "--description",
        type=str,
        nargs="*",
        default="None",
        help="Description, optional"
    )
    ap.add_argument(
        "-l",
        "--locator",
        type=str,
        default="None",
        help="DIMM locator: A B"
    )
    ap.add_argument(
        "-st",
        "--sfp-type",
        type=str,
        default="None",
        help="SFP type: FC / ETH"
    )
    ap.add_argument(
        "--node",
        type=str,
        default="None",
        help="Node number"
    )
    ap.add_argument(
        "--drive-type",
        type=str,
        nargs="*",
        default="None",
        help="Drive type: Enclosure Drive, Local Drive, SSD"
    )
    args = ap.parse_args()
    if "None" not in args.drive_type:
        args.drive_type = " ".join(args.drive_type)
    if "None" not in args.rejection:
        args.rejection = " ".join(args.rejection)
    else:
        args.rejection = ""
    if "None" not in args.description:
        args.description = " ".join(args.description)
    else:
        args.description = ""
    args.noLogs = [True, False][args.noLogs == "false"]
    return args


def get_component(args, ibox):
    if ("sa" or "switch") not in args.component:
        node_connection = get_node_connection(ibox)

    if "enclosure" in args.component:
        return Enclosure(node_connection, args.part_name)
    elif "iom" in args.component:
        return IOM(node_connection, args.part_name, args.side)
    elif "pcm" in args.component:
        return PCM(node_connection, args.part_name, args.side)
    elif "pdu" in args.component:
        return PDU(ibox.connect_to_sa(), args.part_name)
    elif "ups" in args.component:
        return UPS(ibox.connect_to_node(args.part_name), args.part_name, ibox)
    elif "sa" in args.component:
        try:
            return SA(ibox.connect_to_sa(), 1)
        except NoValidConnectionsError:
            try:
                return SA(ibox.connect_to_node(1), 1)
            except NoValidConnectionsError:
                print("Could not connect to the SA or the nodes, please check and try again.")
                exit
    elif "switch" in args.component:
        return Switch(ibox.connect_to_sa(), 1)
    elif "nmc" in args.component:
        return UpsNmc(ibox.connect_to_sa(), args.part_name, ibox)
    elif "node" in args.component:
        return Node(ibox.connect_to_node(args.part_name), args.part_name)
    elif "dimm" in args.component:
        return DIMM(ibox.connect_to_node(args.node), args.part_name, args.locator, int(args.node))
    elif "sfp" in args.component:
        return SFP(ibox.connect_to_node(args.node), args.part_name, args.sfp_type, int(args.node))
    elif "drive" in args.component:
        if "Enclosure Drive" in args.drive_type:
            return EnclosureDrive(node_connection, args.part_name, args.drive_type)
        elif "Local Drive" in args.drive_type:
            return LocalDrive(ibox.connect_to_node(args.node), args.part_name, args.drive_type, int(args.node))
        elif "SSD" in args.drive_type:
            return SSD(ibox.connect_to_node(args.node), args.part_name, args.drive_type, int(args.node))
    elif "1u" in args.component:
        return UtilityDrawer(None, 1)
    elif "ats" in args.component:
        return ATS(None, args.part_name)


def get_node_connection(ibox):
    try:  # try connecting to any node available and keep the connection before passing each function
        connection = ibox.connect_to_node(1)
    except socket.timeout as s:
        print("Can't connect to Node-1, attempting to connect to Node-2 \n", s)
        try:
            connection = ibox.connect_to_node(2)
        except socket.timeout as s:
            print("Can't connect to Node-2, attempting to connect to Node-3 \n", s)
            try:
                connection = ibox.connect_to_node(3)
            except socket.timeout as s:
                print("Can't connect to any of the nodes, check connection", s)
                sys.exit(1)
    return connection
