
import boto3
from config import Config
from botocore.exceptions import ClientError
import os
from exceptions import SubnetNotFoundError
from exceptions import ImageNotFoundError
from vm import VirtualMachine


class EC2Wrapper:

    def __init__(self):
        cfg = Config()
        cfg.load(os.path.join(os.path.dirname(__file__), 'vm_manager.cfg'), 'aws')
        access_key_id = cfg.get('access_key_id')
        secret_access_key = cfg.get('secret_access_key')
        region = cfg.get('region')

        self.client = boto3.client('ec2', aws_access_key_id=access_key_id,
                                   aws_secret_access_key=secret_access_key,
                                   region_name=region)
        self.ec2 = boto3.resource('ec2', aws_access_key_id=access_key_id,
                                  aws_secret_access_key=secret_access_key,
                                  region_name=region)

    def find_by_name(self, arr, name):
        found = None
        for item in arr:
            names = [tag['Value'] for tag in item['Tags'] if tag['Key'] == 'Name']
            if len(names) > 0 and names[0] == name:
                found = item
                break
        return found

    def get_all_my_images(self):
        return self.client.describe_images(Owners=['self'])['Images']

    def get_image_by_name(self, image_name):
        matched_image = None
        images = [image for image in self.get_all_my_images() if image['Name'] == image_name]
        if len(images) > 0:
            matched_image = images[0]
        return matched_image

    def get_all_subnets(self):
        return self.client.describe_subnets()['Subnets']

    def get_subnet_by_name(self, name):
        return self.find_by_name(self.get_all_subnets(), name)

    def get_all_security_groups(self):
        return self.client.describe_security_groups()['SecurityGroups']

    def get_security_groups_by_names(self, names):
        return [group for group in self.get_all_security_groups() if group['GroupName'] in names]

    def make_network_interface(self, subnet_name, private_ip, security_groups, index=0):
        subnet = self.get_subnet_by_name(subnet_name)
        if subnet is None:
            raise SubnetNotFoundError()
        security_group_ids = [group['GroupId'] for group in self.get_security_groups_by_names(security_groups)]
        return {
            'DeviceIndex': index,
            'SubnetId': subnet['SubnetId'],
            'PrivateIpAddress': private_ip,
            'AssociatePublicIpAddress': True,
            'Groups': security_group_ids
        }

    def create_instance(self, instance_type, image_name, key_name, network_interface, dryrun=False):
        image = self.get_image_by_name(image_name)
        if image is None:
            raise ImageNotFoundError()
        instance = self.ec2.create_instances(
                        DryRun=dryrun,
                        ImageId=image['ImageId'],
                        MinCount=1, MaxCount=1,
                        KeyName=key_name,
                        InstanceType=instance_type,
                        NetworkInterfaces=[network_interface])[0]
        return VirtualMachine(instance_id=instance.instance_id)

    def get_all_instances(self):
        instances = list()
        reservations = self.client.describe_instances()['Reservations']
        for rsv in reservations:
            if 'Instances' in rsv and len(rsv['Instances']) > 0:
                for instance in rsv['Instances']:
                    instances.append(instance)
        return instances

    def get_instance(self, instance_id):
        instance = None
        try:
            reservations = self.client.describe_instances(
                InstanceIds=[instance_id]
            )['Reservations']
        except ClientError as e:
            return instance

        for rsv in reservations:
            if 'Instances' in rsv and len(rsv['Instances']) > 0:
                instance = rsv['Instances'][0]
        return instance

    def delete_instance(self, instance_id):
        return self.client.terminate_instances(InstanceIds=[instance_id])['TerminatingInstances']
