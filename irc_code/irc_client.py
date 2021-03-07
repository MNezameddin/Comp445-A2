#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
import logging

import patterns
import view
import socket
import select
import argparse
from _thread import start_new_thread

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()
parser = argparse.ArgumentParser()


class IRCClient(patterns.Subscriber):


    def __init__(self):
        super().__init__()
        logger.debug(f"hello there")
        self.host = args.host
        logger.debug(f"added newhost {args.host}")
        self.port = args.port
        self.nick = args.nick
        self.username = args.username
        self._run = True

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        #sends to server
        # usermsg = self.username + ": " + msg
        self.process_input(msg)
        #receives from server
        # data = self.server_socket.recv(512)
        # server_data = data.decode()
        # self.process_input(server_data)      

    def process_input(self, msg):
        # Will need to modify this
        if '/quit' in msg.lower():
            # Command that leads to the closure of the process
            raise KeyboardInterrupt
        else:

            logger.info(f"Sending {msg} message to server")
            

            self.server_socket.sendall(msg.encode())

    def add_msg(self, msg):
        # server_user = msg.split(": ", 1)
        # server_username = server_user[0]
        # server_msg = server_user[1]
        self.view.add_msg(self.username, msg)
    def listen_socket(self):

        self.add_msg('before socket')

        while True:
            try:
                ready = select.select([self.server_socket], [], [], 0.5)

                if ready:
                    logger.debug(f"in listen socket loop")

                    data = self.server_socket.recv(512)

                    self.add_msg(data.decode())
            except KeyboardInterrupt as e:
                logger.debug(f"Signifies end of process")
    async def run(self):
        """
        Driver of your IRC Client
        """
        # welcomeMsg = "Welcome " + self.username + " to #general chat!"
        logger.debug(f"added yuhost {self.host}")
        logger.debug(f"added port {self.port}")
        # self.view.add_msg("Server", welcomeMsg)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"socket added")
        userinfo= "nick:" + self.nick + ":username:" + self.username
        self.server_socket.connect((self.host,int(self.port)))
        logger.debug(f"socket connected")
        self.server_socket.send(userinfo.encode())
        # self.server_socket.setblocking(0)
        start_new_thread(self.listen_socket, ())
                    

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass
            

def main(args):
    # Pass your arguments where necessary
    logger.debug(f"added host {args.host}")
    client = IRCClient()

    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")
        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )            
        try:
            asyncio.run( inner_run() )
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()

if __name__ == "__main__":
    # Parse your command line arguments here
    parser.add_argument("-host", "--host", help="Host")
    parser.add_argument("-port", "--port", help="Port")
    parser.add_argument("-nick", "--nick", help="nick")
    parser.add_argument("-username", "--username", help="port")
    args = parser.parse_args()
    main(args)
