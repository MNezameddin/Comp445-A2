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

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):


    def __init__(self):
        super().__init__()
        print("Please enter your Nick: ")
        self.nick = input()
        print("Please enter your Username: ")
        self.username = input()
        if self.username == "":
            self.username = "Anonymous"

        self._run = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Asking user for HOST input
        print("If you would like to input a Host to connect to, please enter it below. You can press \"Enter\" to use default values.")
        host = input()
        if host == '':
            host = "localhost"
        #Asking user for PORT input
        print("If you would like to input a port to bind to, please enter it below. You can press \"Enter\" to use default values.")
        port = input()
        if port == '':
            port = "8088"

        userinfo= "nick:" + self.nick + ":username:" + self.username
        self.server_socket.connect((host,int(port)))
        self.server_socket.send(userinfo.encode())

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
        usermsg = self.username + ": " + msg
        self.server_socket.sendall(usermsg.encode())
        #receives from server
        data = self.server_socket.recv(512)
        server_data = data.decode()
        self.process_input(server_data)      

    def process_input(self, msg):
        # Will need to modify this
        if '/quit' in msg.lower():
            # Command that leads to the closure of the process
            raise KeyboardInterrupt
        self.add_msg(msg)

    def add_msg(self, msg):
        server_user = msg.split(": ", 1)
        server_username = server_user[0]
        server_msg = server_user[1]
        self.view.add_msg(server_username, server_msg)

    async def run(self):
        """
        Driver of your IRC Client
        """
        welcomeMsg = "Welcome " + self.username + " to #general chat!"
        self.view.add_msg("Server", welcomeMsg)
                    

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
