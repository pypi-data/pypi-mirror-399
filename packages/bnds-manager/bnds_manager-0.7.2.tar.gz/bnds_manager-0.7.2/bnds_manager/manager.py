# Last modified: 2024/02/05 14:42:29

from simplejson.decoder import JSONDecodeError
import requests
import posixpath
from getpass import getpass
from .model import BayesianNetwork
import json
from .interface import InterfaceConfig
from ._version import __version__
from . import errors
from . import _hosts

class ModelManagerMixin:

    # - Model endpoints
    def get_model_list(self):
        return self._get_response('model')        

    def get_my_models(self):
        return self._get_response('user/model')

    def get_model(self, id):
        return self._get_response(f'model/{id}')

    def download_model(self, id, **kwargs):
        data = self._get_response(f'model/{id}/download')
        return BayesianNetwork.from_dict(data, **kwargs)

    def calculate(self, id, inputs={}, outputs=None):

        if outputs is None:
            raise TypeError('Please provide a list of output variables')
        
        data = {
            'inputs': inputs,
            'output_nodes': outputs
        }

        return self._get_response(f'model/{id}/calculate', request_type='post', data=data, status_code=200)

    def save_model(self, id, file, **kwargs):
        model = self.download_model(id, **kwargs)
        model.to_json(file)
        
    @staticmethod
    def _construct_model_data(model):

        if not isinstance(model, BayesianNetwork):
            raise TypeError('The supplied model must be a mini-zest BayesianNetwork object')

        return model.to_dict()

    def create_model(self, model):
        return self._get_response('model/create', request_type='post', data=self._construct_model_data(model))

    def update_model(self, model):
        return self._get_response(f'model/{model.id}/update', request_type='put', data=self._construct_model_data(model))

    def create_or_update_model(self, model):
        
        try:
            response = self.create_model(model)
        
        except errors.ObjectExistsError:

            response = self.update_model(model)

        return response

    def delete_model(self, id, automate_response=False):
        
        proceed = automate_response

        if not proceed:
            confirmation = input(f"Are you sure you want to delete model '{id}'? [y/n]")
            proceed = confirmation.lower() == 'y'

        if proceed:
            response = self._send_request(f'model/{id}/delete', request_type='delete')

            if response.status_code == 204:
                print('Model deleted')
            else:
                print(response.json())

            return response
    
    def get_model_users(self, id):
        return self._get_response(f'model/{id}/user')

    def add_user_to_model(self, modelId, username, canUpdate=False, canDelete=False):

        data = {            
            'username': username,
            'canView': True,
            'canUpdate': canUpdate,
            'canDelete': canDelete
        }

        return self._get_response(f'model/{modelId}/permission/create', request_type='post', data=data)

    def remove_user_from_model(self, modelId, username):        
        return self._get_response(f"model/{modelId}/permission/{username}/delete", request_type='delete')

class InterfaceManagerMixin:

    """
    Mixin for dealing with interfaces
    """

    def get_interface_list(self):        
        return self._get_response('interface')
    
    def get_interface(self, interfaceId):
        return self._get_response(f'interface/{interfaceId}')

    def get_my_interfaces(self):
        return self._get_response(f'user/interface')

    def download_interface(self, interfaceId):
        data = self._get_response(f'interface/{interfaceId}/download')
        return InterfaceConfig.from_dict(data)
    
    def save_interface(self, interfaceId, file):
        interface = self.download_interface(interfaceId)        
        interface.to_json(file)

    @staticmethod
    def _construct_interface_data(interface):

        if not isinstance(interface, InterfaceConfig):
            raise TypeError('The supplied config must be an InterfaceConfig object')

        return interface.to_dict()

    def create_interface(self, interface):
        print("create_interface:",interface.to_dict())
        return self._get_response('interface/create', request_type='post', data=self._construct_interface_data(interface))

    def update_interface(self, interface):
        return self._get_response(f"interface/{interface.id}/update", request_type='put', data=self._construct_interface_data(interface))

    def create_or_update_interface(self, interface):

        try:
            response = self.create_interface(interface)
        
        except errors.ObjectExistsError or ValueError:

            response = self.update_interface(interface)
            
        return response

    def delete_interface(self, id, automate_response=False):

        proceed = automate_response

        if not proceed:
            confirmation = input(f"Are you sure you want to delete interface '{id}'? [y/n]")
            proceed = confirmation.lower() == 'y'

        if proceed:
            response = self._send_request(f'interface/{id}/delete', request_type='delete')

            if response.status_code == 204:
                print('Interface deleted')
            else:
                print(response.json())

            return response


    def get_interface_users(self, id):
        return self._get_response(f'interface/{id}/user')

    def add_user_to_interface(self, interfaceId, username, canUpdate=False, canDelete=False):

        data = {            
            'username': username,
            'canView': True,
            'canUpdate': canUpdate,
            'canDelete': canDelete
        }

        return self._get_response(f'interface/{interfaceId}/permission/create', request_type='post', data=data)

    def remove_user_from_interface(self, interfaceId, username):        
        return self._get_response(f"interface/{interfaceId}/permission/{username}/delete", request_type='delete')


class Manager(ModelManagerMixin, InterfaceManagerMixin):

    """
    Manager for BNDS interaction. Supports production and development sites

    Examples:
    1. Use default host and manually enter username and password
    manager = Manager()

    2. Use alternative host and provide username and password, e.g.
    manager = Manager(host='local')

    or 

    manager = Manager(host='http://127.0.0.1:3000')
    
    3. Create manager from JSON file with keys host (optional), username and password
    manager = Manager.from_file('path/to/file.json')
    
    """

    access_token = None
    refresh_token = None
    user = None
    _version = None
    
    def __init__(self, host='local', username=None, password=None):

        self.host = getattr(_hosts, host) if host in dir(_hosts) else host

        self.username = input('Enter username: ') if username is None else username
        self.password = getpass('Enter password: ') if password is None else password

        self.fetch_details()

    def _get_url(self, route):
        return posixpath.join(self.host, route)

    def fetch_details(self):

        response = requests.post(
            self._get_url('auth/login'),
            headers={
                'bnds_manager_version': self._get_version()
            },
            json={
                'username': self.username,
                'password': self.password
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            del data['access_token']
            del data['refresh_token']
            self.user = data
        else:
            try:
                msg = response.json()

                if hasattr(errors, msg['type']):
                    raise getattr(errors, msg['type'])(msg['message'])
                else:
                    raise ValueError(msg)
                    
            except JSONDecodeError:
                raise ValueError(f'There was a problem logging in to the server at {self.host}')
            
    def _get_version(self):
        return __version__ if (self._version is None) else self._version

    def get_access_token(self):

        if self.access_token is None:
            self.fetch_details()
        
        return self.access_token

    def _send_request(self, route, request_type='get', data=None):

        response = getattr(requests, request_type)(url=self._get_url(route), headers={'Authorization': f'Bearer {self.get_access_token()}'}, json=data)
        # print("REQUEST DATA:\n" + str(data) + "\n ")
        if response.status_code == 401:
            
            refresh_response = requests.post(
                self._get_url('auth/refresh'),
                json={
                    'username': self.username,
                    'refresh_token': self.refresh_token
                }
            )

            if refresh_response.status_code == 200:

                self.access_token = refresh_response.json()['access_token']
                return self._send_request(route, request_type=request_type, data=data)
            
            else:

                return refresh_response

        return response

    def _get_response(self, route, request_type='get', data=None, status_code=None):
        response = self._send_request(route=route, request_type=request_type, data=data)

        code_mappings = {
            'get': 200,
            'post': 201,
            'put': 200,
            'delete': 204
        }

        if status_code is None:
            status_code = code_mappings[request_type]

        if response.status_code == status_code:
            try:
                return response.json()
            except JSONDecodeError:
                return response
        else:
            try:
                msg = response.json()
                
                print("manager.py response code after _get_response call:\n", response)

                if hasattr(errors, msg['type']):
                    raise getattr(errors, msg['type'])(msg['message'])
                else:
                    raise ValueError(msg) # TODO: This error is being raised in the server too. we need to make exceptions for subwidgets

            except JSONDecodeError:
                print(response)

            return response

    def get_bnds_users(self):
        return self._get_response('user')
    
    def get_user(self, username):
        return self._get_response(f'user/{username}')

    def create_user(self, username, password, first_name, last_name, staff=False, superuser=False):
        data = {
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'staff': staff,
            'superuser': superuser
        }
        return self._get_response('user/create', request_type='post', data=data)

    def update_user(self, username, password, first_name, last_name, staff=False, superuser=False):
        data = {
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'staff': staff,
            'superuser': superuser
        }
        return self._get_response(f'user/{username}/update', request_type='put', data=data)

    def delete_user(self, username):
        response = self._get_response(f'user/{username}/delete', request_type='delete')
        if response.status_code == 204:
            print(f'User {username} deleted')
        else:
            print(response.json())
        return response

    @classmethod
    def from_file(cls, file):
        data = json.loads(open(file, 'r').read())
        return cls(**data)

    def __repr__(self) -> str:
        return f'Manager ({self.username})'