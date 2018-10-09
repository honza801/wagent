# Test connection to localhost zmq REP via ssh tunnel

import sys
import zmq
import zmq.ssh

context = zmq.Context()

socket = context.socket(zmq.REQ)
#socket.connect("tcp://127.0.0.1:5555")
tunnel = zmq.ssh.tunnel_connection(socket, "tcp://127.0.0.2:5555", "127.0.0.1", paramiko=True)

client = ""
if len(sys.argv) > 1:
    client = sys.argv[1]

#  Do 10 requests, waiting each time for a response
for request in range(3):
    print(tunnel)
    req = u'Req from {} no.{}'.format(client, request)
    print("Sending request: {}".format(req))
    socket.send(bytes(req, 'utf-8'))

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))
