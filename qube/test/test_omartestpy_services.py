#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['OMARTESTPY_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['OMARTESTPY_MONGOALCHEMY_SERVER'] = ''
    os.environ['OMARTESTPY_MONGOALCHEMY_PORT'] = ''
    os.environ['OMARTESTPY_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.omartestpy import omartestpy
    from qube.src.services.omartestpyservice import omartestpyService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, omartestpyServiceError


class TestomartestpyService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.omartestpyService = omartestpyService(context)
        self.omartestpy_api_model = self.createTestModelData()
        self.omartestpy_data = self.setupDatabaseRecords(self.omartestpy_api_model)
        self.omartestpy_someoneelses = \
            self.setupDatabaseRecords(self.omartestpy_api_model)
        self.omartestpy_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.omartestpy_someoneelses.save()
        self.omartestpy_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.omartestpy_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.omartestpy_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, omartestpy_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy_data = omartestpy(name='test_record')
            for key in omartestpy_api_model:
                omartestpy_data.__setattr__(key, omartestpy_api_model[key])

            omartestpy_data.description = 'my short description'
            omartestpy_data.tenantId = "23432523452345"
            omartestpy_data.orgId = "987656789765670"
            omartestpy_data.createdBy = "1009009009988"
            omartestpy_data.modifiedBy = "1009009009988"
            omartestpy_data.createDate = str(int(time.time()))
            omartestpy_data.modifiedDate = str(int(time.time()))
            omartestpy_data.save()
            return omartestpy_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_omartestpy(self, *args, **kwargs):
        result = self.omartestpyService.save(self.omartestpy_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.omartestpy_api_model['name'])
        omartestpy.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy(self, *args, **kwargs):
        self.omartestpy_api_model['name'] = 'modified for put'
        id_to_find = str(self.omartestpy_data.mongo_id)
        result = self.omartestpyService.update(
            self.omartestpy_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.omartestpy_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy_description(self, *args, **kwargs):
        self.omartestpy_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.omartestpy_data.mongo_id)
        result = self.omartestpyService.update(
            self.omartestpy_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.omartestpy_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy_item(self, *args, **kwargs):
        id_to_find = str(self.omartestpy_data.mongo_id)
        result = self.omartestpyService.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(omartestpyServiceError):
            self.omartestpyService.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy_list(self, *args, **kwargs):
        result_collection = self.omartestpyService.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.omartestpy_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy_data.mongo_id)
        with self.assertRaises(omartestpyServiceError) as ex:
            self.omartestpyService.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy_data.mongo_id)
        self.omartestpyService.auth_context.is_system_user = True
        self.omartestpyService.delete(id_to_delete)
        with self.assertRaises(omartestpyServiceError) as ex:
            self.omartestpyService.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.omartestpyService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy_someoneelses.mongo_id)
        with self.assertRaises(omartestpyServiceError):
            self.omartestpyService.delete(id_to_delete)
