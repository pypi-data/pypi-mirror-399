# Last modified: 2024/02/05 15:25:40

import re
import json
from .tables import PriorProbabilityTable, ConditionalProbabilityTable
import numpy as np
import uuid



class State(object):
    """
    Represents a state in an HMM. Holds emission distribution, but not
    transition distribution, because that's stored in the graph edges.
    """

    def __init__(self, distribution, name=None, weight=None):
        """
        Make a new State emitting from the given distribution. If distribution
        is None, this state does not emit anything. A name, if specified, will
        be the state's name when presented in output. Name may not contain
        spaces or newlines, and must be unique within a model.
        """

        # Save the distribution
        self.distribution = distribution

        # Save the name
        self.name = name or str(uuid.uuid4())

        # Save the weight, or default to the unit weight
        self.weight = weight or 1.

    def __str__(self):
        """
        The string representation of a state is the json, so call that format.
        """
        return self.to_json()

    def __repr__(self):
        """
        The string representation of a state is the json, so call that format.
        """
        return self.__str__()

    def copy(self):
        """Return a hard copy of this state."""
        return State(distribution=self.distribution.copy(), name=self.name)

    def to_dict(self):
        """Convert this state to a dictionary of parameters."""
        return {
            'class': 'State',
            'distribution': None if self.is_silent() else self.distribution.to_dict(),
            'name': self.name,
            'weight': self.weight
        }

    def to_json(self, separators=(',', ' : '), indent=4):
        """Convert this state to JSON format."""
        return json.dumps(self.to_dict(), separators=separators, indent=indent)

    @classmethod
    def from_json(cls, s):
        """Read a State from a given string formatted in JSON."""

        # Load a dictionary from a JSON formatted string
        return cls.from_dict(json.loads(s))




class Node(State):

    def __init__(self, name, states, parents=None, npt=None, id=None, group=None, description=None):

        self.parents = parents
        self.states = states

        if npt is None:
            npt = 'uniform'

        if isinstance(npt, str):

            if npt in ['random', 'uniform']:
                shape = [len(self.states), *self.parent_sizes()]
                npt = getattr(self, f'_{npt}_npt')(*shape)
            else:
                raise ValueError(f'The keyword {npt} for the argument npt is not recognised')

        if self.prior():
            distribution = PriorProbabilityTable(
                label=name,
                states=self.states,
                values=npt
            )
        else:
            distribution = ConditionalProbabilityTable(
                label=name,
                states=self.states,
                parent_nodes=self.parents,
                values=npt
            )

        super().__init__(distribution, name)

        self.id = re.sub(r'[^a-z0-9_]', '', self.name.lower())[:20] if (id is None) else id
        self.group = group
        self.description = description

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not re.match(r'[a-z0-9_]{1,20}$', value):
            raise ValueError(f'The id {value} must be at most 20 characters consisting of lowercase letters, numbers and underscores')

        self.__id = value

    @property
    def states(self):
        return self.__states

    @states.setter
    def states(self, states):
        if (states is None) or (states == 'YN'):
            self.__states = ['No', 'Yes']
        elif states == 'PN':
            self.__states = ['Negative', 'Positive']
        elif states == 'TF':
            self.__states = ['False', 'True']
        else:
            self.__states = states

    def parent_sizes(self):
        parents = [] if (self.parents is None) else self.parents
        return [len(parent) for parent in parents]

    def parent_names(self):
        parents = [] if (self.parents is None) else self.parents
        return [parent.name for parent in parents]

    def prior(self):
        return self.parents is None

    @property
    def npt(self):
        return self.distribution

    @npt.setter
    def npt(self, values):
        self.distribution.values = values

    def to_dict(self):
        
        data = {
            'id': self.id,
            'name': self.name,
            'states': self.states,
            'group': self.group,
            'description': self.description
        }

        data['parents'] = None if (self.parents is None) else [parent.id for parent in self.parents]
        data['npt'] = self.npt.to_df().values.tolist()
        
        return data

    @staticmethod
    def _random_npt(*args):
        npt = np.random.rand(*args)
        return npt/npt.sum(axis=0)

    @staticmethod
    def _uniform_npt(*args):
        npt = np.ones(args)
        return npt/npt.sum(axis=0)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self):
        return f"Node('{self.id}')"

    def __repr__(self):
        return self.id

    def __len__(self):
        return len(self.states)
    
