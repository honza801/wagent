import zmq
import json
from json.decoder import JSONDecodeError
import subprocess
import shutil
import logging
from rbd import RBD

bind_to = 'tcp://127.0.0.2:5555'
log_level = logging.INFO

class WAException(Exception):
    def __init__(self, message, exitcode):
        self.message = message
        self.exitcode = exitcode

class WebvirtcloudAgent():
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(bind_to)
        logging.info("Socket binds to {}".format(bind_to))
        self.rbd = RBD()
        while True:
            self.handle_request()
    
    def handle_request(self):
        #  Wait for next request from client
        request = self.socket.recv()

        try:
            reply = self.try_action(request)
            self.send_reply(reply)
        except WAException as e:
            logging.warning(e.message)
            self.send_reply(e.message, e.exitcode)
        except Exception as e:
            logging.exception(e)
            msg = '{}: {}'.format(type(e).__name__, e.args[0])
            self.send_reply(msg)
    
    def send_reply(self, reply, exitcode=0):
        if type(reply) == bytes:
            reply = reply.decode('utf-8')
        rep = { 'message': reply, 'exitcode': exitcode }
        logging.debug(rep)
        rep_str = json.dumps(rep)
        self.socket.send(bytes(rep_str, 'utf-8'))

    def format_action(self, request):
        action_json = json.loads(request.decode('utf-8'))
        return action_json

    def try_action(self, request):
        action = self.format_action(request)
        logging.debug('try_action action: {}'.format(action))
        
        if not 'action' in action.keys():
            msg = "Action undefined"
            raise WAException(msg, 101)

        if action['action'] == 'rbd':
            return self._action_rbd(action)
        else:
            msg = "Unsupported action: {}".format(action['action'])
            raise WAException(msg, 102)
    
    def _action_rbd(self, action):
        ac_sub = action['subaction'][0]
        if ac_sub == 'clone':
            return self.rbd.clone(action['source'], action['target'])
        if ac_sub == 'snap':
            ac_snap = action['subaction'][1]
            if ac_snap == 'list':
                return self.rbd.snap_list(action['image'])
            elif ac_snap == 'create':
                return self.rbd.snap_create(action['image'], action['snap_name'])
            elif ac_snap == 'rollback':
                return self.rbd.snap_rollback(action['image'], action['snap_name'])
            elif ac_snap == 'remove':
                return self.rbd.snap_remove(action['image'], action['snap_name'])
            else:
                msg = "Unsupported subaction '{}'".format(action['subaction'][1])
                raise WAException(msg, 104)
        else:
            msg = "Unsupported subaction '{}'".format(action['subaction'][0])
            raise WAException(msg, 103)


if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    wa = WebvirtcloudAgent()
 
