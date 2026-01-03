# Last modified: 2024/02/05 15:30:30

import json
import re
import numpy as np
from .parsers import from_cmpx, to_cmpx, from_dict

class BayesianNetwork(object):

    def __init__(self, name, description=None, variables=None, **kwargs):
        self.name = name
        self.states = []
        self.edges = []
        self.graph = None
        self.n_edges = 0
        self.n_states = 0

        self.add_nodes(*variables)

        self._check_variable_ids()

        if description is not None:
            self.description = description

        for variable in filter(lambda x: not x.prior(), self.variables):
            for parent in variable.parents:
                self.add_edge(parent, variable)

        # Set id
        if 'id' not in kwargs:

            value = re.sub(r'[^a-z0-9_]', '', self.name.lower())[:20]
            self.id = value

        # Set remaining kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not re.match(r'^[a-z0-9_]{1,20}$', value):
            raise ValueError(f'The id {value} must be at most 20 characters consisting of lowercase letters, numbers and underscores')

        self.__id = value

    def get_params(self, *args, **kwargs):
        return self.__getstate__()

    def set_params(self, state):
        self.__setstate__(state)

    @staticmethod
    def _check_groups(groups, form):

        msg = f"{form} groups must be a list of dictionaries of the form {{id, name, description}}"

        if not isinstance(groups, list):
            raise TypeError(msg)
        
        if not all(isinstance(d, dict) for d in groups):
            raise TypeError(msg)
        
        for group in groups:
            if not set(group.keys()) == {'id', 'name', 'description'}:
                raise TypeError(msg)

        id_list = [g['id'] for g in groups]

        if len(np.unique(id_list)) != len(id_list):
            raise TypeError(f"The ids of {form} groups must be unique")

    @property
    def input_groups(self):
        return self.__input_groups
    
    @input_groups.setter
    def input_groups(self, groups):        
        self._check_groups(groups, 'input')
        self.__input_groups = groups

    @property
    def output_groups(self):
        return self.__output_groups
    
    @output_groups.setter
    def output_groups(self, groups):
        self._check_groups(groups, 'output')
        self.__output_groups = groups

    @property
    def variables(self):
        return self.states

    @property
    def variable_names(self):
        return [x.name for x in self.states]

    @property
    def variable_ids(self):
        return [x.id for x in self.states]

    def _check_variable_ids(self):
        var_ids = self.variable_ids
        if len(np.unique(var_ids)) < len(var_ids):
            raise ValueError('The ids of the provided variables are not unique')
        
    @classmethod
    def from_cmpx(cls, filename, network=0, **kwargs):
        
        """
        Returns BayesianNetwork model from cmpx file

        Args:
        filename (str) - path to cmpx
        
        Kwargs:
        network [=0] (int) - specifies which network to use

        Optional kwargs:
        remove_disconnected_variables [=True] (bool) - removes any disconnected variables from the model
        force_summation [=False] - forces values of the npt to equal 1
        """

        with open(filename, 'r') as file:
            data_string = file.read()

        return cls(**from_cmpx(json.loads(data_string), network=network, **kwargs))

    @classmethod
    def from_dict(cls, data, **kwargs):
                
        """
        Returns BayesianNetwork model from  dict

        Args:
        data (dict) - model data in dictionary form
    
        Optional kwargs:
        force_summation [=False] - forces values of the npt to equal 1
        """

        return cls(**from_dict(data, **kwargs))

    @classmethod
    def from_json(cls, filename, **kwargs):
        
        """
        Returns BayesianNetwork model from json file

        Args:
        filename (str) - path to json
        
        Optional kwargs:
        force_summation [=False] - forces values of the npt to equal 1
        """

        with open(filename, 'r') as file:
            data_string = file.read()
           
        return cls.from_dict(json.loads(data_string), **kwargs)

    def to_cmpx(self, filename):
        data = json.dumps(to_cmpx(self), indent=2)
        with open(filename, 'w') as file:
            file.write(data)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,            
        }

        for key in ['description', 'input_groups', 'output_groups']:
            if hasattr(self, key):
                data[key] = getattr(self, key)
        
        data['variables'] = [variable.to_dict() for variable in self.variables]        
        return data

    def to_json(self, filename=None):

        json_string = json.dumps(self.to_dict(), indent=2)

        if filename is None:
            return json_string
        else:
            with open(filename, 'w') as file:
                file.write(json_string)

    def __getitem__(self, item):
        return self.states[self.variable_ids.index(item)]

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return f'BayesianNetwork({self.name})'

    def add_node(self, node):
        """Add a node to the graph."""
        self.states.append(node)
        self.n_states += 1

    def add_nodes(self, *nodes):
        """Add multiple states to the graph."""
        for node in nodes:
            self.add_node(node)

    def add_edge(self, a, b):
        """
        Add a transition from state a to state b which indicates that B is
        dependent on A in ways specified by the distribution.
        """

        # Add the transition
        self.edges.append((a, b))
        self.n_edges += 1

    def node_count(self):
        """Returns the number of nodes/states in the model"""
        return self.n_states

    def edge_count(self):
        """Returns the number of edges present in the model."""
        return self.n_edges

    def copy(self):
        """Return a deep copy of this object.
        """

        return self.__class__(*self.parameters)
