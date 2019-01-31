
import json


class VirtualMachine:

    def __init__(self, instance_id=None, type=None, private_ip=None, status=None):
        self.instance_id = instance_id
        self.type = type
        self.private_ip = private_ip
        self.status = status

    def load(self, payload):
        if isinstance(payload, str):
            payload = json.loads(payload)
        self.instance_id = payload['InstanceId']
        self.type = payload['InstanceType']
        self.status = payload['State']['Name']
        if self.status != 'terminated':
            self.private_ip = payload['PrivateIpAddress']
        return self

    def from_dict(self, **entries):
        self.__dict__.update(entries)
        return self
