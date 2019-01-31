
import pymysql.cursors
from config import Config
import os
from vm import VirtualMachine
from exceptions import InvalidParameterTypeError
import logging
from flask import current_app


class DBWrapper:

    def __init__(self):
        cfg = Config()
        cfg.load(os.path.join(os.path.dirname(__file__), 'vm_manager.cfg'), 'database')
        self.connection = pymysql.connect(host=cfg.get('host'),
                                          port=int(cfg.get('port')),
                                          user=cfg.get('user'),
                                          password=cfg.get('password'),
                                          db=cfg.get('db_name'),
                                          cursorclass=pymysql.cursors.DictCursor)
        self.logger = logging.getLogger(current_app.name)
        self.logger.info('Connected to DB.')

    def close(self):
        self.connection.close()
        self.logger.info('DB connection closed.')

    def select_all_slaves(self):
        c = self.connection.cursor()
        c.execute('SELECT * FROM slave')
        return c.fetchall()

    def select_slave_by_instance_id(self, instance_id):
        c = self.connection.cursor()
        c.execute("SELECT * FROM slave WHERE instance_id = '%s'" % instance_id)
        return c.fetchone()

    def select_last_ip(self):
        last_ip = None
        c = self.connection.cursor()
        c.execute('SELECT private_ip FROM slave')
        ip_list = c.fetchall()
        self.logger.debug('Fetched ip list from db: %s' % ip_list)
        if ip_list is not None and len(ip_list) > 0:
            max_value = 0
            for ip in ip_list:
                arr = ip['private_ip'].rsplit('.', 1)
                if int(arr[-1]) >= max_value:
                    max_value = int(arr[-1])
                    last_ip = ip['private_ip']
        return last_ip

    def get_next_ip(self):
        next_ip = None
        last_ip = self.select_last_ip()
        if last_ip is not None:
            arr = last_ip.rsplit('.', 1)
            arr[-1] = str(int(arr[-1]) + 1)
            next_ip = '.'.join(arr)
        return next_ip

    def update_slave_status(self, instance_id, status):
        updated = False
        c = self.connection.cursor()
        try:
            c.execute("UPDATE slave SET status = '%s' WHERE instance_id = '%s'" % (status, instance_id))
            if c.rowcount > 0:
                self.connection.commit()
                updated = True
        except:
            self.connection.rollback()
        return updated

    def insert_slave(self, vm):
        if not isinstance(vm, VirtualMachine):
            raise InvalidParameterTypeError()
        instance_id = None
        c = self.connection.cursor()
        try:
            c.execute("INSERT INTO slave(instance_id, type, private_ip, status, created_at) " + \
                      "VALUES('%s', '%s', '%s', '%s', now())" % \
                      (vm.instance_id, vm.type, vm.private_ip, vm.status))
            if c.lastrowid > 0:
                self.connection.commit()
                instance_id = vm.instance_id
        except:
            self.connection.rollback()
        return instance_id

    def delete_slave(self, instance_id):
        deleted = False
        c = self.connection.cursor()
        try:
            c.execute("DELETE FROM slave WHERE instance_id = '%s'" % instance_id)
            if c.rowcount > 0:
                self.connection.commit()
                deleted = True
        except:
            self.connection.rollback()
        return deleted
