import socket
import select
import time

class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)
        host, port = 'localhost', 8080
        self.server_socket.bind((host, port))
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
        try:
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
                    # reading from clients
                    else:
                        data = r.recv(self.read_size).decode('utf-8')
                        if data:
                            print("Received data: {}".format(data))
                            self.messages[r] += data
                            self._parse_message(r)
                        else:
                            print("Removing client socket from watchlists")
                            self.potential_reads.remove(r)
                            if r is self.outbox:
                                del self.outbox[r]
                            if r is self.messages:
                                del self.messages[r]
                            print("Closed a client socket: {}".format(r))
                            r.close()
                for w in r_writes:
                    msg = self.outbox[w]
                    if len(msg):
                        print("Sending message to client: {}".format(w))
                        w.send(msg.encode())
                        self._clear_outbox(w)
                for err in r_errors:
                    self.potential_reads.remove(err)
                    if err is self.outbox:
                        del self.outbox[err]
                    if err is self.messages:
                        del self.messages[err]
        except KeyboardInterrupt:
            print("\nServer interrupted, closing socket connections")
        except:
            pass
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