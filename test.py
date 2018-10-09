# Test connection to localhost zmq REP via ssh tunnel

import sys
import zmq
import zmq.ssh
import json

context = zmq.Context()

socket = context.socket(zmq.REQ)
#socket.connect("tcp://127.0.0.1:5555")
tunnel = zmq.ssh.tunnel_connection(socket, "tcp://127.0.0.2:5555", "127.0.0.1", paramiko=True)
print(tunnel)

client = ""
if len(sys.argv) > 1:
    client = sys.argv[1]

def send_request(req):
    print("Sending request [ %s ]" % req)
    socket.send(bytes(req, 'utf-8'))
    message = socket.recv()
    print("Received reply [ %s ]" % (message))
    
req = u'Req from {}'.format(client)
send_request(req)

rbd_create = { 'image': 'flat' }
send_request(json.dumps(rbd_create))

rbd_create = { 'action': 'ac', 'subaction': 'flat' }
send_request(json.dumps(rbd_create))

rbd_create = { 'action': 'rbd', 'subaction': 'none' }
send_request(json.dumps(rbd_create))

rbd_create = {
    'action': 'rbd',
    'subaction': ['snap', 'list'],
    'image': 'novejimages',
    'snap_name': 'snap1'
}
send_request(json.dumps(rbd_create))
