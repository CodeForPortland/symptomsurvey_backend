import os
import tempfile
import flask_pymongo
import json
import hashlib

import pytest
from unittest.mock import create_autospec

from app import create_app
from services import auth_service, database_service


# Load the values from the constants file.  This file contains the parameters that are used for the
# hashing algorithim that is applied to the salted passwords.
with open('constants.json') as f:
    salt_constants = json.load(f)['salt']

def get_nested_key(dictionary, key_list):
  result = dictionary
  for key in key_list.split('.'):
    if not result.get(key):
      return None
    else:
      result = result.get(key)

  return result

def search_datum(search, datum):
  for key in search.keys():
    if get_nested_key(datum, key) != search[key]:
      return False
  
  return True

class UsersCollection:
  def __init__(self, name):
    self.name = name
    
    with open('seeds/{0}.json'.format(name)) as seed:
      base_data = json.load(seed)
    
    self.data = []
    for user in base_data:
      new_user = user
      salt = 'thing'
      new_user['password'] = {'salt': salt, 'hash': hashlib.pbkdf2_hmac(salt_constants['algorithm'], bytes(user['password'], 'utf-8'), bytes(salt, 'utf-8'), int(salt_constants['iterations']), dklen=int(salt_constants['key_length']))}

  def find(self, search):
    if not search:
      return self.data

    result = []
    for datum in self.data:
      if search_datum(search, datum):
        result.append(datum)
    
    return result

class Collection:
  def __init__(self, name):
    self.name = name
    
    with open('seeds/{0}.json'.format(name)) as seed:
      self.data = json.load(seed)

  def find(self, search):
    if not search:
      return self.data

    result = []
    for datum in self.data:
      if search_datum(search, datum):
        result.append(datum)
    
    return result

class Database:
  def __init__(self):
    self.users = UsersCollection('users')
    self.roles = Collection('roles')

class TestConfig:
  class __MongoSession:
    class __MongoClient:
      def __init__(self):
        self.db = Database()

    def __init__(self):
      self.mongo = self.__MongoClient()

  def start_test_session(self):
    database_service.MongoSession(self.__MongoSession())

@pytest.fixture(scope='session')
def client():
  return create_app(testconfig = TestConfig()).test_client()

def test_root_path(client):
  assert client.get('/').data == b'Hello, World!'
  assert client.get('/').status == '200 OK'