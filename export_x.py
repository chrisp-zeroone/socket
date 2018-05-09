#!/usr/bin/env python
# Builtin
import socket
import logging

# Third-party
try:
    from maya import cmds
except ImportError:
    pass

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

HOST = socket.gethostname()
PORT = 19723


class Client(object):
    """ Client to host transfer of info from maya """
    def __init__(self, host=None, port=None):
        self.host = host or HOST
        self.port = port or PORT
        self.items = []
        self.auto_exp = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # TODO check for auto_exp in scene already!

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((self.host, self.port))

    def add_item(self, item):
        """ Add item to list to be exported"""
        self.items.append(item)

    def rem_item(self, item):
        """ Add item to list to be exported"""
        self.items.remove(item)

    def send(self, data):
        """ Send info through the socket"""
        if not data:
            LOG.warn("No data to send")
        self.sock.sendto(data, (self.host, self.port))

    def get_values(self):
        """ Create a string of x values"""
        return " ".join([str(cmds.xform(item, q=True, t=True)[0]) for item in self.items])

    def send_values(self):
        """ Do all the stuff """
        self.send(self.get_values())

    def auto_send(self):
        self.auto_exp = cmds.expression(string='python("win.widget.client.send_values()")')

    def del_exp(self):
        cmds.delete(self.auto_exp)

    def disconnect(self):
        self.sock.close()


class Server(object):
    """ Server meant to echo commands provided """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', PORT))

    def launch(self):
        while True:
            try:
                data, address = self.sock.recvfrom(1024)
                if not data:
                    print 'no data'
                    break
                print "Client Says: "+data
            except socket.error:
                print "Error Occured."
                break


if __name__ == '__main__':
    serv = Server()
    serv.launch()

