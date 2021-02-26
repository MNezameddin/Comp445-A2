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

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):


    def __init__(self):
        super().__init__()
        print("Please enter your Username: ")
        self.username = input()
        self._run = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #change the host according to OS 
        print("If you would like to input a Host to connect to, please enter it below. You can press \"Enter\" to use default values.")
        host = input()
        if host == '':
            host = "localhost"
        print("If you would like to input a port to bind to, please enter it below. You can press \"Enter\" to use default values.")
        port = input()
        if port == '':
            port = "8088"
        self.server_socket.connect((host,int(port)))
        self.server_socket.sendall(b'Hello, world')

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
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        """
        Driver of your IRC Client
        """
        self.add_msg("Welcome to #general chat!")

        

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):
    # Pass your arguments where necessary
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
    args = None
    main(args)
