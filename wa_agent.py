import zmq
import json
import subprocess
import shutil
import logging

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
        while True:
            self.handle_request()
    
    def handle_request(self):
        #  Wait for next request from client
        request = self.socket.recv()

        try:
            reply = self.try_action(request)
            self.send_reply(reply)
        except WAException as e:
            logging.debug(e.message)
            self.send_reply(e.message, e.exitcode)
        except Exception as e:
            logging.exception(e)
            msg = '{}: {}'.format(type(e).__name__, e.args[0])
            self.send_reply(msg)
    
    def send_reply(self, reply, exit=0):
        rep = { 'message': reply, 'exit': exit }
        rep_str = json.dumps(rep)
        self.socket.send(bytes(rep_str, 'utf-8'))

    def format_action(self, request):
        action_json = json.loads(request.decode('utf-8'))
        return action_json

    def get_command(self, action):
        logging.debug('build_command: {}'.format(action))
        if not 'action' in action.keys():
            msg = "Action undefined"
            raise WAException(msg, 101)
        if action['action'] == 'rbd':
            return self._get_rbd_command(action)
        else:
            msg = "Unsupported action: {}".format(action['action'])
            raise WAException(msg, 102)

    def _get_rbd_command(self, action):
        cmd = []
        cmdpath = self.which_command(action['action'])
        cmd.append(cmdpath)
        if action['subaction'][0] == 'snap':
            cmd.extend(action['subaction'])
            snapshot_name = "{image}@{snap_name}".format(**action)
            cmd.append(snapshot_name)
            return cmd
        else:
            msg = "Unsupported subaction '{}'".format(action['subaction'][0])
            raise WAException(msg, 103)
    
    def which_command(self, cmd):
        cmdpath = shutil.which(cmd)
        if cmdpath:
            return cmdpath
        raise Exception("Command '{}' not found".format(cmd))

    def try_action(self, request):
        action = self.format_action(request)
        logging.debug('try_action action: {}'.format(action))
        
        cmd = self.get_command(action)
        
        logging.debug('try_action cmd: {}'.format(cmd))
        cmdout = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmdout.returncode > 0:
            raise WAException(cmdout.stderr, cmdout.returncode)
        if cmdout.stdout:
            return cmdout.stdout
        else:
            return "Command executed successfully"


if __name__ == '__main__':
    logging.basicConfig(level=log_level)
    wa = WebvirtcloudAgent()
    main()
 
