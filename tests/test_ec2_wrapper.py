
import unittest
from aws_ec2 import EC2Wrapper
from aws_ec2 import SubnetNotFoundError
from aws_ec2 import ImageNotFoundError


class TestEC2Wrapper(unittest.TestCase):

    def setUp(self):
        self.wrapper = EC2Wrapper()

    def tearDown(self):
        super().tearDown()

    def test_find_by_name(self):
        name = 'testname'
        arr = [
            {
                'Tags': [
                    {'Key': 'Name', 'Value': name}
                ]
            }
        ]
        found = self.wrapper.find_by_name(arr, name)
        self.assertIsNotNone(found)
        self.assertFalse(isinstance(found, list))

    def test_get_image_by_name(self):
        image = self.wrapper.get_image_by_name('test')
        self.assertIsNone(image)
        image = self.wrapper.get_image_by_name('mesos-slave-base-ami')
        self.assertIsNotNone(image)

    def test_get_subnet_by_name(self):
        subnet = self.wrapper.get_subnet_by_name('test')
        self.assertIsNone(subnet)
        subnet = self.wrapper.get_subnet_by_name('codealley-pub-subnet1')
        self.assertIsNotNone(subnet)

    def test_get_security_groups_by_names(self):
        self.assertTrue(len(self.wrapper.get_security_groups_by_names('test')) == 0)
        self.assertIsNotNone(self.wrapper.get_security_groups_by_names('default'))
        security_groups = self.wrapper.get_security_groups_by_names(['default', 'was-sg'])
        self.assertIsNotNone(security_groups)
        self.assertTrue(len(security_groups) == 2)

    def test_make_network_interface(self):
        with self.assertRaises(SubnetNotFoundError):
            self.wrapper.make_network_interface('test_subnet', '10.1.100.101', 'default')

        ip = '10.1.100.101'
        nif = self.wrapper.make_network_interface('codealley-pub-subnet1', ip, 'default')
        self.assertIsNotNone(nif)
        self.assertTrue(nif['PrivateIpAddress'] == ip)

    def test_create_instance(self):
        nif = self.wrapper.make_network_interface('codealley-pub-subnet1', '10.1.100.101', 'default')
        with self.assertRaises(Exception) as context:
            self.wrapper.create_instance('t2.micro', 'test_image', 'codealley_aws_oregon', nif, dryrun=True)
        self.assertEqual(context.exception.__class__.__name__, ImageNotFoundError.__name__)

        with self.assertRaises(Exception) as context:
            self.wrapper.create_instance('t2.micro', 'mesos-slave-base-ami', 'codealley_aws_oregon', nif, dryrun=True)
        self.assertTrue(context.exception.response['Error'].get('Code') == 'DryRunOperation')

    '''
    def test_get_instance_status(self):
        with self.assertRaises(Exception) as context:
            self.wrapper.get_instance_status('instance_id')
        self.assertTrue(context.exception.response['Error'].get('Code') == 'InvalidInstanceID.Malformed')
    '''

    def test_delete_instance(self):
        with self.assertRaises(Exception) as context:
            self.wrapper.delete_instance('instance_id')
        self.assertTrue(context.exception.response['Error'].get('Code') == 'InvalidInstanceID.Malformed')

    def test_get_all_instances(self):
        instances = self.wrapper.get_all_instances()
        self.assertIsNotNone(instances)
        for instance in instances:
            self.assertIsNotNone(instance['InstanceId'])
            print(instance['InstanceId'])

    def test_get_instance(self):
        instance = self.wrapper.get_instance('test_instance_id')
        self.assertIsNone(instance)
        instances = self.wrapper.get_all_instances()
        self.assertIsNotNone(instances)
        for instance in instances:
            print('test:' + instance['InstanceId'])
            self.assertIsNotNone(instance['InstanceId'])
            retrieved = self.wrapper.get_instance(instance['InstanceId'])
            print('retrieved:' + retrieved['InstanceId'])
            self.assertIsNotNone(retrieved)
            self.assertTrue(retrieved['InstanceId'] == instance['InstanceId'])


if __name__ == '__main__':
    unittest.main()
