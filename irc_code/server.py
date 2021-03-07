import socket
import select
import time
import argparse

class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)
        parser = argparse.ArgumentParser()
        parser.add_argument("-port", "--port", help="Port")
        args = parser.parse_args()
        port = args.port
        host = "localhost"

        self.server_socket.bind((host, int(port)))
        self.server_socket.listen(0)
        self.read_size = 512

        #Select Vars
        self.potential_reads = list()
        self.potential_reads.append(self.server_socket)
        self.potential_writes = list()
        self.potential_errors = list()
        self.outbox = dict()
        self.messages = dict()

        

    def run(self):
        print("Server running...")
        channel_log= dict()
        while True:
            r_reads, r_writes, r_errors= select.select(self.potential_reads, self.potential_writes, self.potential_errors)
            for r in r_reads:
                #server socket accepting clients
                if r is self.server_socket:
                    client_socket, addr = r.accept()
                    client_socket.setblocking(False)
                    print("New client @ {}".format(addr))
                    self.outbox[client_socket] = list()
                    self.messages[client_socket] = str()
                    self.potential_reads.append(client_socket)
                #reading from clients
                else:
                    data = r.recv(self.read_size).decode('utf-8')
                    if data:
                        if 'nick:' in data:
                            nick_message = data.split(":")
                            nickname = nick_message[1]
                            username = nick_message[3]
                            #checks if NICK exists in dictionary
                            if nickname in channel_log.values():
                                print("Unable to register Client with same NICK!")
                                self.potential_reads.remove(r)
                                r.close()
                            else:
                                channel_log[r] = nickname
                                print("Successfully added "+channel_log[r]+" to the server!")
                            
                        else:
                            print("Received data: {}".format(data))
                            self.messages[r] += data
                            self._parse_message(r)
                            for x in self.potential_reads[1:]:
                                x.sendall(data.encode())
                    else:
                        print("Removing client socket from watchlists")
                        if r in channel_log:
                            channel_log.pop(r)
                        self.potential_reads.remove(r)
                        if r is self.outbox:
                            del self.outbox[r]
                        if r is self.messages:
                            del self.messages[r]
                        print("Closed a client socket: {}".format(r))
                        r.close()
        self.close()

    def _clear_outbox(self, client_socket):
        if client_socket in self.outbox:
            self.outbox[client_socket] = str()

    def close(self):
        for s in self.potential_reads:
            s.close()

    def _parse_message(self, client):
        pass
    
if __name__ == "__main__":
    server = Server()
    server.run()