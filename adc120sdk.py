
import zmq

import time
import json


class AdcControl:

    # default constructor
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.streamsocket = self.context.socket(zmq.PULL)
        self.streameventssocket = self.context.socket(zmq.PULL)

    def connect(self, address):
        self.socket.connect(address)

    def connect_data(self, address):
        self.streamsocket.connect(address)

    def connect_events(self, address):
        self.streameventssocket.connect(address)

    def set_timeout(self, timeout):
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.streamsocket.setsockopt(zmq.RCVTIMEO, timeout)
        self.streameventssocket.setsockopt(zmq.RCVTIMEO, timeout)

    def set_parameter(self, param, value, index=0):
        request = {
            "command": "set_parameter",
            "name": param,
            "idx": index,
            "value": str(value)
        }
        self.socket.send(bytes(json.dumps(request), 'utf-8'))
        response = self.socket.recv()
        rj = json.loads(response)
        if rj["response"] != "ok":
            raise Exception({"code" : rj["error_code"], "message":  rj["message"]})

    def get_parameter(self, param, index=0):
        request = {
            "command": "get_parameter",
            "name": param,
            "idx": index
        }
        self.socket.send(bytes(json.dumps(request), 'utf-8'))
        response = self.socket.recv()
        rj = json.loads(response)
        if rj["response"] != "ok":
            raise Exception({"code" : rj["error_code"], "message":  rj["message"]})
        else:
            return rj["value"]

    def execute_cmd(self, cmd, args=""):
        request = {
            "command": "execute_cmd",
            "name": cmd,
            "args" : args
        }
        self.socket.send(bytes(json.dumps(request), 'utf-8'))
        response = self.socket.recv()
        rj = json.loads(response)
        if rj["response"] != "ok":
            raise Exception({"code" : rj["error_code"], "message":  rj["message"]})

    def read_data(self, name, args=""):
        request = {
            "command": "execute_read_command",
            "name": name,
            "args" : args
        }
        self.socket.send(bytes(json.dumps(request), 'utf-8'))
        response = self.socket.recv()
        rj = json.loads(response)
        if rj["response"] != "ok":
            raise Exception({"code" : rj["error_code"], "message":  rj["message"]})
        else:
            return rj["data"]

    def get_data(self):
        return self.streamsocket.recv()

    def get_events(self):
        return self.streameventssocket.recv()        
    