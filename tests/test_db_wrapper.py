import unittest
from db_wrapper import DBWrapper
from vm import VirtualMachine
from exceptions import InvalidParameterTypeError


class TestDBWrapper(unittest.TestCase):

    def setUp(self):
        self.wrapper = DBWrapper()

    def tearDown(self):
        self.wrapper.close()

    def test_select_all_slaves(self):
        slaves = self.wrapper.select_all_slaves()
        print(slaves)
        if slaves is not None:
            for slave in slaves:
                print(slave)
                self.assertIsNotNone(slave['instance_id'])
                self.assertIsNotNone(slave['type'])
                self.assertIsNotNone(slave['private_ip'])
                self.assertIsNotNone(slave['status'])
                self.assertIsNotNone(slave['created_at'])

    def test_select_slave_by_instance_id(self):
        slave = self.wrapper.select_slave_by_instance_id('test_instance_id')
        print(slave)
        self.assertIsNone(slave)
        slaves = self.wrapper.select_all_slaves()
        if slaves is not None:
            for slave in slaves:
                selected = self.wrapper.select_slave_by_instance_id(slave['instance_id'])
                print(selected)
                self.assertIsNotNone(selected)

    def test_select_last_ip(self):
        slaves = self.wrapper.select_all_slaves()
        last_ip = self.wrapper.select_last_ip()
        print('last ip:' + last_ip)
        if slaves is not None:
            self.assertIsNotNone(last_ip)
            for slave in slaves:
                ip = slave['private_ip']
                self.assertTrue(int(last_ip.split('.')[-1]) >= int(ip.split('.')[-1]))
        else:
            self.assertIsNone(last_ip)

    def test_update_slave_status(self):
        updated = self.wrapper.update_slave_status('test_instance', 'running')
        self.assertFalse(updated)
        slaves = self.wrapper.select_all_slaves()
        if slaves is not None:
            for slave in slaves:
                instance_id = slave['instance_id']
                selected = self.wrapper.select_slave_by_instance_id(instance_id)
                old_status = selected['status']
                new_status = 'pending' if old_status == 'running' else 'running'
                updated = self.wrapper.update_slave_status(instance_id, new_status)
                self.assertTrue(updated)
                updated_status = self.wrapper.select_slave_by_instance_id(instance_id)['status']
                self.assertEqual(updated_status, new_status)
                print('instance:%s old_status:%s new_status:%s updated_status:%s' %\
                      (instance_id, old_status, new_status, updated_status))
                self.wrapper.update_slave_status(instance_id, old_status)

    def test_insert_delete_slave(self):
        with self.assertRaises(InvalidParameterTypeError):
            self.wrapper.insert_slave('invalid_parameter')

        vm = VirtualMachine(instance_id='test_instance_id', type='t2.micro',\
                            private_ip=self.wrapper.get_next_ip(), status='pending')
        inserted_instance_id = self.wrapper.insert_slave(vm)
        self.assertIsNotNone(inserted_instance_id)
        selected = self.wrapper.select_slave_by_instance_id(inserted_instance_id)
        self.assertIsNotNone(selected)
        deleted = self.wrapper.delete_slave(selected['instance_id'])
        self.assertTrue(deleted)


if __name__ == '__main__':
    unittest.main()
