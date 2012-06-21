#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import copy
import numpy as np
from ..lib import gravity
from ..lib.utils.timing import decallmethods, timings


__all__ = ['Pbase']


def with_properties(cls):
    def make_property(attr, doc):
        def fget(self): return self.data[attr]
        def fset(self, value): self.data[attr] = value
        def fdel(self): raise NotImplementedError()
        return property(fget, fset, fdel, doc)
    attrs = ((i[0], cls.__name__+'\'s '+i[2]) for i in cls.attributes)
    for (attr, doc) in attrs:
        setattr(cls, attr, make_property(attr, doc))
    return cls


@decallmethods(timings)
class Pbase(object):
    """

    """
    attributes = None
    attrs = None
    dtype = None
    zero = None

    def __init__(self, n=0):
        self.data = np.zeros(n, self.dtype) if n else self.zero


    #
    # miscellaneous methods
    #

    def __repr__(self):
        fmt = self.__class__.__name__+'['
        if self:
            fmt += '\n'
            for item in self:
                if item:
                    fmt += '(\n'
                    for name in self.data.dtype.names:
                        fmt += '{0} = {1},\n'.format(name, getattr(item, name).tolist())
                    fmt += '),\n'
        fmt += ']'
        return fmt

    def __len__(self):
        return len(self.data)
    n = property(__len__)

    def __getitem__(self, index):
        obj = self.__class__()
        obj.data = self.data[index]
        return obj

    def copy(self):
        return copy.deepcopy(self)

    def append(self, obj):
        self.data = np.append(self.data, obj.data)

    def remove(self, id):
        index = np.where(self.id == id)
        self.data = np.delete(self.data, index)

    def insert(self, index, obj):
        self.data = np.insert(self.data, index, obj.data)

    def pop(self, id=None):
        if id:
            index = np.where(self.id == id)
        else:
            index = -1
        obj = self[index]
        self.data = np.delete(self.data, index)
        return obj

    def get_state(self):
        return self.data[self.attrs]

    def set_state(self, state):
        self.data = np.zeros(len(state), dtype=self.dtype)
        for name in state.dtype.names:
            if name in self.data.dtype.names:
                self.data[name] = state[name]

    def astype(self, cls):
        obj = cls()
        obj.set_state(self.get_state())
        return obj

    def stack_fields(self, attrs, pad=-1):
        arrays = []
        for attr in attrs:
            arr = self.data[attr]
            arrays.append(arr.reshape(-1,1) if arr.ndim < 2 else arr)

        array = np.concatenate(arrays, axis=1)

        ncols = array.shape[1]
        col = ncols - pad
        if col < 0:
            pad_array = np.zeros((len(array),pad), dtype=array.dtype)
            pad_array[:,:col] = array
            return pad_array
        if ncols > 1:
            return array
        return array.squeeze()


    #
    # common methods
    #

    ### total mass and center-of-mass

    def get_total_mass(self):
        """
        Get the total mass.
        """
        return float(np.sum(self.mass))

    def get_center_of_mass_position(self):
        """
        Get the center-of-mass position.
        """
        mtot = self.get_total_mass()
        return (self.mass * self.pos.T).sum(1) / mtot

    def get_center_of_mass_velocity(self):
        """
        Get the center-of-mass velocity.
        """
        mtot = self.get_total_mass()
        return (self.mass * self.vel.T).sum(1) / mtot

    def correct_center_of_mass(self):
        """
        Correct the center-of-mass to origin of coordinates.
        """
        self.pos -= self.get_center_of_mass_position()
        self.vel -= self.get_center_of_mass_velocity()


    ### linear momentum

    def get_individual_linear_momentum(self):
        """
        Get the individual linear momentum.
        """
        return (self.mass * self.vel.T).T

    def get_total_linear_momentum(self):
        """
        Get the total linear momentum.
        """
        return self.get_individual_linear_momentum().sum(0)


    ### angular momentum

    def get_individual_angular_momentum(self):
        """
        Get the individual angular momentum.
        """
        return (self.mass * np.cross(self.pos, self.vel).T).T

    def get_total_angular_momentum(self):
        """
        Get the total angular momentum.
        """
        return self.get_individual_angular_momentum().sum(0)


    ### kinetic energy

    def get_individual_kinetic_energy(self):
        """
        Get the individual kinetic energy.
        """
        return 0.5 * self.mass * (self.vel**2).sum(1)

    def get_total_kinetic_energy(self):
        """
        Get the total kinetic energy.
        """
        return float(np.sum(self.get_individual_kinetic_energy()))


    ### potential energy

    def get_individual_potential_energy(self):
        """
        Get the individual potential energy.
        """
        return self.mass * self.phi

    def get_total_potential_energy(self):
        """
        Get the total potential energy.
        """
        return 0.5 * float(np.sum(self.get_individual_potential_energy()))


    ### update methods

    def update_nstep(self):
        """
        Update individual step number.
        """
        self.nstep += 1

    def update_t_curr(self, tau):
        """
        Evolves individual current time by tau.
        """
        self.t_curr += tau


    ### gravity

    def update_phi(self, objs):
        """
        Update individual gravitational potential due j-particles.
        """
        gravity.phi.set_args(self, objs)
        gravity.phi.run()
        self.phi = gravity.phi.get_result()

    def update_acc(self, objs):
        """
        Update individual gravitational acceleration due j-particles.
        """
        gravity.acc.set_args(self, objs)
        gravity.acc.run()
        self.acc = gravity.acc.get_result()

    def update_tstep(self, objs, eta):
        """
        Update individual time-step due j-particles.
        """
        gravity.tstep.set_args(self, objs, eta/2)
        gravity.tstep.run()
        self.dt_next = gravity.tstep.get_result()

    def update_acc_jerk(self, objs):
        """
        Update individual gravitational acceleration and jerk due j-particles.
        """
        gravity.acc_jerk.set_args(self, objs)
        gravity.acc_jerk.run()
        (self.acc, self.jerk) = gravity.acc_jerk.get_result()


########## end of file ##########
