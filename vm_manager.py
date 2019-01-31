
from flask import Flask
from flask import abort
from flask import request
from aws_ec2 import EC2Wrapper
from vm import VirtualMachine
import json
from db_wrapper import DBWrapper
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
import pprint

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('vm_manager.log', maxBytes=1024*1024*10, backupCount=10)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s  %(message)s'))
logger.addHandler(handler)


@app.route('/vms', methods=['GET'])
def get_vms():
    logger.info('Requested to get all vms.')
    wrapper = EC2Wrapper()
    instances = [VirtualMachine().load(instance) for instance in wrapper.get_all_instances()]
    for i in instances:
        logger.info(i.__dict__)
    return json.dumps([instance.__dict__ for instance in instances])


@app.route('/vms/<instance_id>', methods=['GET'])
def get_vm(instance_id):
    logger.info('Requested to get vm which has id %s', instance_id)
    wrapper = EC2Wrapper()
    instance = wrapper.get_instance(instance_id)
    logger.info(pprint.pformat(instance))
    if instance is None:
        logger.error('Get instance error.')
        abort(404)
    else:
        return json.dumps(VirtualMachine().load(instance).__dict__)


@app.route('/vms/<instance_id>', methods=['DELETE'])
def delete_vm(instance_id):
    logger.info('Requested to delete vm which has id %s', instance_id)
    wrapper = EC2Wrapper()
    results = wrapper.delete_instance(instance_id)
    logger.info(pprint.pformat(results))
    if results is not None and len(results) > 0:
        deleted_id = results[0]['InstanceId']
        db_wrapper = DBWrapper()
        db_wrapper.delete_slave(deleted_id)
        db_wrapper.close()
        return json.dumps(VirtualMachine(instance_id=deleted_id).__dict__)
    else:
        logger.error('Delete instance error.')
        abort(404)


@app.route('/vms', methods=['POST'])
def create_vm():
    instance_type = json.loads(str(request.data, 'utf-8'))['type']
    logger.info('Requested to create vm type: %s', instance_type)
    if instance_type is None or not instance_type:
        logger.error('Invalid parameter.')
        abort(400)

    # retrieve slave list from db
    db_wrapper = DBWrapper()
    ip = db_wrapper.get_next_ip()
    logger.info('Private ip to be allocated: %s', ip)

    # make network interface
    cfg = Config()
    cfg.load(os.path.join(os.path.dirname(__file__), 'vm_manager.cfg'), 'codealley')
    ec2_wrapper = EC2Wrapper()
    nif = ec2_wrapper.make_network_interface(cfg.get('subnet'), ip, cfg.get('security_groups').split(','))
    logger.info('Network interface to be created: %s', pprint.pformat(nif))

    # create vm
    created = ec2_wrapper.create_instance(instance_type, cfg.get('image'), cfg.get('key'), nif)
    if created is None:
        logger.error('Create instance error.')
        abort(500)
    else:
        info = ec2_wrapper.get_instance(created.instance_id)
        vm = VirtualMachine(instance_id=info['InstanceId'], type=info['InstanceType'],
                            private_ip=info['PrivateIpAddress'], status=info['State']['Name'])
        logger.info('Created vm info: %s', vm.__dict__)
        # insert vm info to db
        db_wrapper.insert_slave(vm)
        db_wrapper.close()
        return json.dumps(vm.__dict__)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s  %(message)s',
                        level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
