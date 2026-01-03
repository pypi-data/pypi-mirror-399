#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import json
import os
from slixfeed.config import Data
#from slixfeed.utility.logger import UtilityLogger
import socket
import sys

#logger = UtilityLogger(__name__)

def send_command(ss, command, address):
    data = {
        "address" : address,
        "command" : command
    }
    # Send request
    data_serialied = json.dumps(data)
    ss.sendall(data_serialied.encode("utf-8"))
    # Wait for response
    datastream = ss.recv(1024)
    return datastream.decode("utf-8")

def start():
    """
    Inter-Process Communication interface of type Berkeley sockets.
    """
    parser = ArgumentParser(description="Slixfeed Inter-Process Communication.")

    parser.add_argument(
        "--subscriber",
        dest="subscriber",
        help="an address of a subscriber.",
        metavar="ADDRESS",
        required=True,
        type=str)

    #parser.add_argument(
    #    "--interface",
    #    dest="interface",
    #    help="an interface of a subscriber.",
    #    metavar="INTERFACE",
    #    required=True,
    #    type=str)

    parser.add_argument(
        "--command",
        dest="command",
        help="a command to execute.",
        metavar="COMMAND",
        #nargs="*",
        required=True,
        type=str)

    args = parser.parse_args()

    # IPC socket file location
    directory_data = Data.get_directory()
    filename_ipc_socket = os.path.join(directory_data, "slixfeed.socket")

    # Initiate socket object
    if not os.path.exists(filename_ipc_socket):
        print("IPC socket file does not exist.\n"
              "Please do ensure, that IPC is enabled.\n"
              "Expected location of IPC socket file:\n"
              f"{filename_ipc_socket}")
        sys.exit(-1)

    ss = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ss.connect(filename_ipc_socket)
    address = args.subscriber
    command = args.command
    result = send_command(ss, command, address)
    print(result)
    ss.close()
