#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import copy
import numpy as np
from ..lib.interactor import interact


__all__ = ['Pbase']


class Pbase(object):
    """

    """
    def __init__(self, dtypes, n):
        self.data = np.zeros(n, dtypes)

    #
    # common basic methods
    #

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        cp = self.copy()
        cp.data = item
        return cp

    def copy(self):
        return copy.deepcopy(self)

    def append(self, objs):
        self.data = np.append(self.data, objs.data)

    def remove(self, key):
        index = np.where(self.key == key)
        self.data = np.delete(self.data, index)

    def pop(self, key=None):
        if key:
            index = np.where(self.key == key)
        else:
            index = -1
        item = self[index]
        self.data = np.delete(self.data, index)
        return item

    #
    # common attributes
    #

    #### key ####

    @property
    def key(self):
        return self.data['key']

    @key.setter
    def key(self, values):
        self.data['key'] = values

    @key.deleter
    def key(self):
        raise NotImplementedError()


    #### mass ####

    @property
    def mass(self):
        return self.data['mass']

    @mass.setter
    def mass(self, values):
        self.data['mass'] = values

    @mass.deleter
    def mass(self):
        raise NotImplementedError()


    #### pos ####

    @property
    def pos(self):
        return self.data['pos']

    @pos.setter
    def pos(self, values):
        self.data['pos'] = values

    @pos.deleter
    def pos(self):
        raise NotImplementedError()


    #### vel ####

    @property
    def vel(self):
        return self.data['vel']

    @vel.setter
    def vel(self, values):
        self.data['vel'] = values

    @vel.deleter
    def vel(self):
        raise NotImplementedError()


    #### acc ####

    @property
    def acc(self):
        return self.data['acc']

    @acc.setter
    def acc(self, values):
        self.data['acc'] = values

    @acc.deleter
    def acc(self):
        raise NotImplementedError()


    #### phi ####

    @property
    def phi(self):
        return self.data['phi']

    @phi.setter
    def phi(self, values):
        self.data['phi'] = values

    @phi.deleter
    def phi(self):
        raise NotImplementedError()


    #### eps2 ####

    @property
    def eps2(self):
        return self.data['eps2']

    @eps2.setter
    def eps2(self, values):
        self.data['eps2'] = values

    @eps2.deleter
    def eps2(self):
        raise NotImplementedError()


    #### tcurr ####

    @property
    def tcurr(self):
        return self.data['tcurr']

    @tcurr.setter
    def tcurr(self, values):
        self.data['tcurr'] = values

    @tcurr.deleter
    def tcurr(self):
        raise NotImplementedError()


    #### tnext ####

    @property
    def tnext(self):
        return self.data['tnext']

    @tnext.setter
    def tnext(self, values):
        self.data['tnext'] = values

    @tnext.deleter
    def tnext(self):
        raise NotImplementedError()


    #
    # common methods
    #

    #### center-of-mass ####

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


    #### linear momentum ####

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


    #### angular momentum ####

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


    #### kinetic energy ####

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


    #### potential energy ####

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


    #### gravity ####

    def update_phi(self, objs):
        """
        Update the individual gravitational potential due to other particles.
        """
        self.phi = interact.phi_body(self, objs)[0]     # XXX: phi_body should return only 'phi'

    def update_acc(self, objs):
        """
        Update the individual acceleration due to other particles.
        """
        self.acc = interact.acc_body(self, objs)

    def update_acctstep(self, objs, eta):
        """
        Update the individual acceleration and time-steps due to other particles.
        """
        (self.acc, self.tstep) = interact.acctstep_body(self, objs, eta)

    def update_tstep(self, objs, eta):
        """
        Update the individual time-steps due to other particles.
        """
        self.tstep = interact.tstep_body(self, objs, eta)


    #### evolve ####

    def evolve_pos(self, tstep):
        """
        Evolves position in time.
        """
        self.pos += tstep * self.vel

    def evolve_vel(self, tstep):
        """
        Evolves velocity in time.
        """
        self.vel += tstep * self.acc









###############################################################################
#### XXX: old Pbase

class oldPbase(object):
    """
    A base class implementing common functionalities for all types of particles.
    """
    def __init__(self, numobjs, dtype):
        self._dtype = dtype
        self._data = None
        if numobjs >= 0:
            self._data = np.zeros(numobjs, dtype)
            fields = {}
            for attr in self._dtype['names']:
                fields[attr] = self._data[attr]
            self.__dict__.update(fields)


    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __reversed__(self):
        return reversed(self._data)


    def __getitem__(self, index):
#        if not isinstance(index, slice):
#            index = slice(index, index+1)
        s = self._data[index].copy()
        ret = self.__class__()
        ret.__dict__.update(self.__dict__)
        ret.set_data(s)
        return ret

#    def __getattribute__(self, attr):
#        _dtype = object.__getattribute__(self, '_dtype')
#        if attr in _dtype['names']:
#            _data = object.__getattribute__(self, '_data')
#            return _data[attr]
#        return object.__getattribute__(self, attr)


    def set_data(self, array):
        self._data = array
        fields = {}
        for attr in self._dtype['names']:
            fields[attr] = self._data[attr]
        self.__dict__.update(fields)


    def get_data(self):
        return self._data

    def copy(self):
        ret = self.__class__()
        ret.__dict__.update(self.__dict__)
        ret.set_data(self._data.copy())
        return ret

    def append(self, obj):
        self.set_data(np.concatenate((self._data, obj._data)))

    def insert(self, index, obj):
        self.set_data(np.insert(self._data, index, obj._data))

    def pop(self, index=-1):
        arr = self._data
        item = arr[index]
        self.set_data(np.delete(arr, index))
        return item

#    def remove(self, index):
#        self.set_data(np.delete(self.get_data(), index))


    def fromlist(self, data, dtype):
        self._dtype = dtype
        self._data = None
        if len(data) > 0:
            self._data = np.array(data, dtype)
            fields = {}
            for attr in self._dtype['names']:
                fields[attr] = self._data[attr]
            self.__dict__.update(fields)






########## end of file ##########
