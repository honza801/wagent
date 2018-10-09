import time
import zmq
import json

bind_to = 'tcp://127.0.0.2:5555'
actions_dir = '/etc/webvirtcloud'

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

        #print("cleeping {}".format(message))
        #time.sleep(2)
        action = self.format_action(request)
        if self.check_action(action):
            reply = self.call_action(action)
            self.send_reply(reply)
        else:
            self.send_reply("Cannot call action")
    
    def send_reply(self, reply):
        self.socket.send(bytes(reply, 'utf-8'))

    def format_action(self, request):
        try:
            action_json = json.loads(request)
            return action_json
        except:
            return { 'action': 'invalid' }

    def check_action(self, action):
        if action.has_key('action'):
            if action['action'] == 'rbd':
                return True
        return False

    def call_action(self, action):
        pass


if __name__ == '__main__':
    wa = WebvirtcloudAgent()
    main()
