#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import os
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import socket
import sys

logger = UtilityLogger(__name__)

class GeminiIpc:

    async def server():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename_ipc_socket = os.path.join(publish_properties.directory_data,
                                           "sockets", "gemini.socket")
        # Setup socket
        if os.path.exists(filename_ipc_socket): os.remove(filename_ipc_socket)
        loop = asyncio.get_running_loop()
        ss = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ss.setblocking(False)
        ss.bind(filename_ipc_socket)
        ss.listen(0)
        # conn = None
        # clients = []
        # clients = {}
        # Start listening loop
        while True:
            # Accept "request"
            conn, addr = await loop.sock_accept(ss)
            # # Terminate an old connection in favour of a new connection
            # if len(clients):
            #     for c in clients:
            #         print(c)
            #         c.close()
            #         del c
            # else:
            #     conn, addr = await loop.sock_accept(ss)
            #     clients.append(conn)
            #     print(clients)
            # Manage connections inside a dict
            # fd = conn.fileno()
            # clients[fd] = conn
            # datastream = await loop.sock_recv(conn, 1024)
            # if datastream.decode("utf-8") == "identifier":
            #     await loop.sock_sendall(conn, fd.encode("utf-8"))
            print("A connection from client has been detected. "
                  "Slixfeed is waiting for commands.")
            # print("There are {} clients connected to the IPC "
            #       "interface".format(len(clients)))
            # Process "request"
            while True:
                response = None
                # print("Awaiting for a command")
                # print(clients[fd])
                datastream = await loop.sock_recv(conn, 1024)
                if not datastream: break
                data = datastream.decode("utf-8")
                if "~" in data:
                    data_list = data.split("~")
                    account = data_list[0]
                    command = data_list[1]
                else:
                    command = data
                match command:
                    case _ if command.startswith("gemini:"):
                        information = XmppActions.fetch_gemini(command, account)
                        response = information["message"]
                    case "help":
                        response = XmppActions.print_help()
                    case "help all":
                        response = XmppActions.print_help_list()
                    case _ if (command.startswith("http") and
                               command.endswith(".opml")):
                        response = await XmppActions.import_opml(account, command)
                    case "info":
                        response = XmppActions.print_info_list()
                    case _ if command.startswith("info"):
                        entry = command[5:].lower()
                        response = XmppActions.print_info_specific(entry)
                    case _ if (command.startswith("http") or
                               command.startswith("feed:/") or
                               command.startswith("itpc:/") or
                               command.startswith("rss:/")):
                        information = await XmppActions.fetch_http(command, account)
                        response = information["message"]
                    case "exit":
                        conn.close()
                        break
                    case _:
                        response = XmppActions.print_unknown()
                # Send "response"
                await loop.sock_sendall(conn, response.encode("utf-8"))
        logger.debug(f"{function_name}		Finish")

