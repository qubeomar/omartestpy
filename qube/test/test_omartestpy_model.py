#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class TestomartestpyModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_omartestpy_model(self):
        from qube.src.models.omartestpy import omartestpy
        omartestpy_data = omartestpy(name='testname')
        omartestpy_data.tenantId = "23432523452345"
        omartestpy_data.orgId = "987656789765670"
        omartestpy_data.createdBy = "1009009009988"
        omartestpy_data.modifiedBy = "1009009009988"
        omartestpy_data.createDate = str(int(time.time()))
        omartestpy_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy_data.save()
            self.assertIsNotNone(omartestpy_data.mongo_id)
            omartestpy_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
