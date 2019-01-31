
import unittest
import vm_manager
import json


class TestVMManager(unittest.TestCase):

    def setUp(self):
        self.app = vm_manager.app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_load_config(self):
        config = vm_manager.load_config('../vm_manager.cfg')
        with self.assertRaises(KeyError):
            config.get('test_key')

        self.assertIsNotNone(config.get('image'))
        self.assertIsNotNone(config.get('key'))
        self.assertIsNotNone(config.get('subnet'))
        self.assertIsNotNone(config.get('security_groups'))

    def test_get_vms(self):
        rv = self.app.get('/vms')
        self.assertTrue(rv.status_code == 200)
        self.assertIsNotNone(rv.data)
        data = str(rv.data, 'utf-8')
        raw_list = json.loads(data)
        self.assertTrue(isinstance(raw_list, list))
        for obj in raw_list:
            print(obj)
            self.assertIsNotNone(obj['instance_id'])
            self.assertIsNotNone(obj['type'])
            self.assertIsNotNone(obj['private_ip'])
            self.assertIsNotNone(obj['status'])

    def test_get_vm(self):
        rv = self.app.get('/vms/test_instance')
        self.assertTrue(rv.status_code == 404)

        rv = self.app.get('/vms')
        self.assertTrue(rv.status_code == 200)
        self.assertIsNotNone(rv.data)
        data = str(rv.data, 'utf-8')
        raw_list = json.loads(data)
        self.assertTrue(isinstance(raw_list, list))
        if len(raw_list) > 0:
            vm_id = raw_list[0]['instance_id']
            rv = self.app.get('/vms/%s' % vm_id)
            self.assertTrue(rv.status_code == 200)
            self.assertIsNotNone(rv.data)
            data = str(rv.data, 'utf-8')
            obj = json.loads(data)
            print(obj)
            self.assertIsNotNone(obj['instance_id'])
            self.assertIsNotNone(obj['type'])
            self.assertIsNotNone(obj['private_ip'])
            self.assertIsNotNone(obj['status'])

    # POST /vms
    # DELETE /vms/<instance_id>
    def test_create_delete_vm(self):
        # create test
        rv = self.app.post('/vms', data='{"type": "t2.medium"}')
        print('status code:' + str(rv.status_code))
        self.assertTrue(rv.status_code == 200)
        self.assertIsNotNone(rv.data)
        data = str(rv.data, 'utf-8')
        obj = json.loads(data)
        print(obj)
        self.assertIsNotNone(obj['instance_id'])
        self.assertIsNotNone(obj['type'])
        self.assertIsNotNone(obj['private_ip'])
        self.assertIsNotNone(obj['status'])

        # delete test
        rv = self.app.delete('/vms/%s' % obj['instance_id'])
        self.assertTrue(rv.status_code == 200)
        self.assertIsNotNone(rv.data)
        data = str(rv.data, 'utf-8')
        obj = json.loads(data)
        print(obj)
        self.assertIsNotNone(obj['instance_id'])


if __name__ == '__main__':
    unittest.main()
