
import boto3
import pprint

pp = pprint.PrettyPrinter()
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')


def get_all_vpcs():
    return client.describe_vpcs()['Vpcs']


def get_vpc_by_name(vpc_name):
    matched_vpc = None
    vpcs = get_all_vpcs()
    for vpc in vpcs:
        names = [tag['Value'] for tag in vpc['Tags'] if tag['Key'] == 'Name']
        if len(names) > 0 and names[0] == vpc_name:
            matched_vpc = vpc
            break
    return matched_vpc


def get_all_my_images():
    return client.describe_images(Owners=['self'])['Images']


def get_image_by_name(image_name):
    matched_image = None
    images = [image for image in get_all_my_images() if image['Name'] == image_name]
    if len(images) > 0:
        matched_image = images[0]
    return matched_image


def get_blockdevice_from_image(image_name):
    blockdevice = None
    image = get_image_by_name(image_name)
    if image is not None:
        blockdevice = image['BlockDeviceMapping']
    return blockdevice


def get_all_subnets():
    return client.describe_subnets()['Subnets']


def get_subnet_by_cidr(cidr):
    matched_subnet = None
    subnets = [subnet for subnet in get_all_subnets() if subnet['CidrBlock'] == cidr]
    if len(subnets) > 0:
        matched_subnet = subnets[0]
    return matched_subnet


def get_subnet_by_name(name):
    matched_subnet = None
    subnets = get_all_subnets()
    for subnet in subnets:
        names = [tag['Value'] for tag in subnet['Tags'] if tag['Key'] == 'Name']
        if len(names) > 0 and names[0] == name:
            matched_subnet = subnet
            break
    return matched_subnet


def get_all_security_groups():
    return client.describe_security_groups()['SecurityGroups']


def get_security_groups_by_names(names):
    return [group for group in get_all_security_groups() if group['GroupName'] in names]


def make_network_interface(subnet_name, private_ip, security_groups, index=0):
    subnet = get_subnet_by_name(subnet_name)
    security_group_ids = [ group['GroupId'] for group in get_security_groups_by_names(security_groups) ]
    return {
        'DeviceIndex': index,
        'SubnetId': subnet['SubnetId'],
        'PrivateIpAddress': private_ip,
        'AssociatePublicIpAddress': True,
        'Groups': security_group_ids
    }


def create_instance(instance_type, image_name, key_name, network_interface):
    image = get_image_by_name(image_name)
    return ec2.create_instances(
        ImageId=image['ImageId'],
        MinCount=1,MaxCount=1,
        KeyName=key_name,
        InstanceType=instance_type,
        NetworkInterfaces=[network_interface]
    )


def create_codealley_mesos_slave(private_ip, instance_type='t2.medium'):
    # from config
    image_name = 'mesos-slave-base-ami'
    key_name = 'codealley_aws_oregon'
    subnet_name = 'codealley-pub-subnet1'
    security_groups = ['default', 'mesos-slave-sg', 'zabbix-agent-sg', 'elk-sg']
    # end

    network_interface = make_network_interface(subnet_name, private_ip, security_groups)
    return create_instance(instance_type, image_name, key_name, network_interface)


def get_instance_status(instance_id):
    return client.describe_instance_status(InstanceIds=[instance_id])['InstanceStatuses']


def delete_instance(instance_id):
    return client.terminate_instances(InstanceIds=[instance_id])['TerminatingInstances']


#pp.pprint(get_vpc_by_name('codealley-vpc-oregon')['VpcId'])
#pp.pprint(get_image_by_name('mesos-slave-base-ami'))
#pp.pprint(get_subnet_by_name('codealley-pub-subnet1')['SubnetId'])
#pp.pprint(get_security_groups_by_names(['default', 'elk-sg']))
#pp.pprint(create_codealley_mesos_slave('10.1.100.25'))
#pp.pprint(delete_instance('i-0e3d51298e3be38c3'))
#pp.pprint(get_instance_status('i-0e3d51298e3be38c3'))

# block device
# DeviceNa

# create instance
# DrypRun=True
# ImageId='string'
# MinCount=1
# MaxCount=1
# KeyName='string'
# InstanceType='t2.medium'
# Placement=Placement
# PrivateIpAddress='string'
# SecurityGroupIds=['string', 'string']
# SubnetId='string'
# BlockDeviceMapping=BlockDeviceMapping