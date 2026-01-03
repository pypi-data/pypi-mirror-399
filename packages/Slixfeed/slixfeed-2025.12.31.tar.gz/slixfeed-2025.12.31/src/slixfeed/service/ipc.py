#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.command import UtilityCommand
from slixfeed.utility.logger import UtilityLogger
import socket
import sys

logger = UtilityLogger(__name__)

filename_ipc_socket = os.path.join(
    configurations.directory_data, "slixfeed.socket")

class ServiceIpc:
    """
    Inter-Process Communication server of type Berkeley sockets.
    """
    async def server():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # Setup socket
        if os.path.exists(filename_ipc_socket): os.remove(filename_ipc_socket)
        loop = asyncio.get_running_loop()
        ss = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ss.setblocking(False)
        ss.bind(filename_ipc_socket)
        ss.listen(0)
        # Start a listening loop.
        while True:
            # Accept "request"
            conn, addr = await loop.sock_accept(ss)
            logger.info(f"{function_name}		An IPC request was accepted.")
            # Process "request"
            while conn:
                datastream = await loop.sock_recv(conn, 1024)
                if not datastream: break
                data_serialied = datastream.decode("utf-8")
                data = json.loads(data_serialied)
                address = data["address"]
                command = data["command"]
                response = await UtilityCommand.action(address, command)
                # Send "response"
                await loop.sock_sendall(conn, response.encode("utf-8"))
        logger.debug(f"{function_name}		Finish")
