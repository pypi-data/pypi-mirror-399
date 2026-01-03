# Last modified: 2024/02/05 15:30:48

import pandas as pd
import numpy as np
import itertools

pd.set_option('expand_frame_repr', False)


class PriorProbabilityTable():

    def __new__(cls, label, states, values):
        cls._check_values(label, states, values)
        return super(PriorProbabilityTable, cls).__new__(cls)

    def __init__(self, label, states, values):
        self.label = label
        characters = dict(zip(states, values))
        self.states = characters

        self.name = "DiscreteDistribution"

        self.is_blank_ = True
        self.dtype = None
        if len(characters) > 0:
            self.is_blank_ = False
            self.dtype = self._get_dtype(characters)

        self.dist = characters.copy()
        self.summaries = [{key: 0 for key in characters.keys()}, 0]

    @property
    def values(self):
        return self.parameters[0].values()

    @values.setter
    def values(self, values):
        self._check_values(self.label, self.states, values)
        self.parameters = [dict(zip(self.states, values))]

    @staticmethod
    def _check_values(label, states, values):

        if len(states) != len(values):
            raise ValueError(
                f"The distribution supplied for '{label}' is not the correct shape")

        if abs(sum(values) - 1) > 1e-10:
            raise ValueError(
                f"The probabilities for '{label}' do not sum to 1")

    def _get_dtype(self, characters: dict) -> str:
        """
        Determine dtype from characters.
        """
        return str(type(list(characters.keys())[0])).split()[-1].strip('>').strip("'")
    
    def to_df(self):
        return pd.DataFrame(self.values, index=self.states, columns=[self.label])

    @property
    def parameters(self):
        return [self.dist]

    @parameters.setter
    def parameters(self, parameters):
        d = parameters[0]
        self.dist = d

    def get_params(self, *args, **kwargs):
        return {
            key: getattr(self, key)
            for key in ['label', 'states', 'values']
        }

    def copy(self):
        return self.__class__(**self.get_params())

    def __repr__(self):
        return str(self.to_df().round(3))

    def __str__(self):
        return str(self.to_df().round(3))
    
    def __len__(self):
        return len(self.dist)


class ConditionalProbabilityTable():

    def __init__(self, label, states, parent_nodes, values):
        self.name = "ConditionalProbabilityTable"
        self.summaries = []


        self.label = label
        self.states = states
        self.parent_nodes = parent_nodes
        self.npt_shape = [len(states)] + [len(node)
                                          for node in self.parent_nodes]

        if isinstance(values, list):
            values = np.array(values)

        self._check_values(values)
        params = self._values_to_parameters(values)

        parents = [p.distribution for p in self.parent_nodes]
        table = params


        self.m = len(parents) if parents is not None else len(table[0])-2 # m is the number of parents
        self.n = len(table)                                               # n is the number of parameters
        self.k = len(set(row[-2] for row in table))                       # k is the dimension o fthe last variable (there must be at least one) 


        self.column_idxs = np.arange(self.m+1, dtype='int32')
        self.n_columns = self.m + 1

        self.dtypes = []
        for column in table[0]:
            dtype = str(type(column)).split()[-1].strip('>').strip("'")
            self.dtypes.append(dtype)

        self.parents = parents
        self.parameters = [table, self.parents]

    def parent_labels(self):
        return [parent.label for parent in self.parents]

    def state_list(self):
        return [parent.states for parent in self.parent_nodes] + [self.states]

    @property
    def values(self):
        params = np.array(self.parameters[0])[:, -1]
        shape = [len(parent) for parent in self.parents] + [len(self)]
        params = params.astype(float).reshape(shape)
        return np.moveaxis(params, -1, 0)

    @values.setter
    def values(self, values):

        if isinstance(values, list):
            values = np.array(values)

        self.parameters[0] = self._values_to_parameters(values)

    def _check_values(self, values):

        if not np.array_equal(self.npt_shape, values.shape):
            raise ValueError(
                f"The distribution supplied for '{self.label}' should be of shape {self.npt_shape}")

        f = np.abs(values.sum(axis=0) - 1) > 1e-10
        if any(f.flatten()):
            raise ValueError(
                f"The probabilities for '{self.label}' do not sum to 1")

    def _values_to_parameters(self, values):
        values = np.moveaxis(values, 0, -1).flatten()
        state_combs = list(itertools.product(*self.state_list()))
        return [list(states) + [float(value)] for states, value in zip(state_combs, values)]

    def to_df(self):

        values = self.values.reshape(
            self.npt_shape[0], np.prod(self.npt_shape[1:]))

        levels = (parent.states for parent in self.parent_nodes)
        headings = pd.MultiIndex.from_product(
            levels, names=self.parent_labels())

        return pd.DataFrame(values, index=self.states, columns=headings)

    def get_params(self, *args, **kwargs):
        return {
            key: getattr(self, key)
            for key in ['label', 'states', 'parent_nodes', 'values']
        }

    def to_dict(self):
     
        table, _ = self.parameters

        # list of the values of 'this' variable from the given table 
        value_list = [ row[-2] for row in table]

        # map from 
        param_map = {}
        for state in value_list:
            if not (state in param_map.keys()) :
                param_map[state]= []

        for row in table:
            state = row[-2]
            param_map[state].append(row[-1])

        npt = [param_map[state] for state in param_map.keys()]
 
        return {
            'class' : 'CPT',
            'name' : 'ConditionalProbabilityTable',
            'table' : npt,
            'dtypes' : self.dtypes,
            'parents' : self.parents
        }
    
    def copy(self):
        return self.__class__(**self.get_params())

    def __repr__(self):
        return str(self.to_df().round(3))

    def __str__(self):
        return str(self.to_df().round(3))
    
    def __len__(self):
        return self.k
