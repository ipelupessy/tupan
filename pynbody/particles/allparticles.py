#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from __future__ import print_function
import sys
import copy
import numpy as np
from .sph import Sph
from .body import Body
from .blackhole import BlackHole
from .pbase import AbstractNbodyMethods
from ..lib import gravity
from ..lib.utils.timing import decallmethods, timings


__all__ = ["Particles"]


ALL_PARTICLE_TYPES = ["sph", "body", "blackhole"]


def make_common_attrs(cls):
    def make_property(attr, doc):
        def fget(self):
            seq = [getattr(obj, attr) for obj in self.objs if obj.n]
            if len(seq) == 1:
                return seq[0]
            if len(seq) > 1:
                return np.concatenate(seq)
            return np.concatenate([getattr(obj, attr) for obj in self.objs])
        def fset(self, value):
            for obj in self.objs:
                if obj.n:
                    getattr(obj, attr)[:] = value[:obj.n]
                    value = value[obj.n:]
        def fdel(self):
            raise NotImplementedError()
        return property(fget, fset, fdel, doc)
    attrs = ((i[0], cls.__name__+'\'s '+i[2]) for i in cls.common_attrs)
    for (attr, doc) in attrs:
        setattr(cls, attr, make_property(attr, doc))
    return cls



@decallmethods(timings)
@make_common_attrs
class Particles(AbstractNbodyMethods):
    """
    This class holds the particle types in the simulation.
    """
    def __init__(self, nstar=0, nbh=0, nsph=0):
        """
        Initializer
        """
        self.keys = []
        self.objs = []
        self.n = 0

        if nstar:
            self.body = Body(nstar)
            self.keys.append('body')
            self.objs.append(self.body)
            self.n += nstar

        if nbh:
            self.blackhole = BlackHole(nbh)
            self.keys.append('blackhole')
            self.objs.append(self.blackhole)
            self.n += nbh

        if nsph:
            self.sph = Sph(nsph)
            self.keys.append('sph')
            self.objs.append(self.sph)
            self.n += nsph


    def _setup_obj(self, key, n=0):
        if key == 'body':
            self.body = Body(n)
            self.keys.append('body')
            self.objs.append(self.body)
            self.n += n

        if key == 'blackhole':
            self.blackhole = BlackHole(n)
            self.keys.append('blackhole')
            self.objs.append(self.blackhole)
            self.n += n

        if key == 'sph':
            self.sph = Sph(n)
            self.keys.append('sph')
            self.objs.append(self.sph)
            self.n += n


    @property
    def items(self):
        return zip(self.keys, self.objs)


    #
    # miscellaneous methods
    #

    def __str__(self):
        fmt = type(self).__name__+'(['
        for (key, obj) in self.items:
            fmt += '\n{0},'.format(obj)
        fmt += '\n])'
        return fmt


    def __repr__(self):
        return str(dict(self.items))


    def __contains__(self, name):
        return name in self.__dict__


    def __getitem__(self, name):
        if name not in self: self._setup_obj(name)
        return getattr(self, name)


    def __hash__(self):
        i = None
        for obj in self.objs:
            if i is None:
                i = hash(obj)
            else:
                i ^= hash(obj)
        return i


    def __len__(self):
        return sum([obj.n for obj in self.objs])


    def append(self, objs):
        if isinstance(objs, Particles):
            if objs.n:
                for (key, obj) in objs.items:
                    if obj.n:
                        self[key].append(obj)
                self.n = len(self)
        elif isinstance(objs, (Body, BlackHole, Sph)):
            if objs.n:
                key = type(objs).__name__.lower()
                self[key].append(objs)
                self.n = len(self)
        else:
            raise TypeError("{} can not append obj: {}".format(type(self).__name__, type(objs)))


    def select(self, slc):
        if slc.all(): return self
        if slc.any():
            subset = type(self)()
            for (key, obj) in self.items:
                if obj.n:
                    subset.append(obj[slc[:obj.n]])
                    slc = slc[obj.n:]
            return subset
        return type(self)()


    #
    # uncommon methods
    #

    ### total mass and center-of-mass

    def get_total_rcom_pn_shift(self):
        """

        """
        mtot = self.get_total_mass()
        rcom_shift = 0.0
        for obj in self.objs:
            if obj.n:
                if hasattr(obj, "get_rcom_pn_shift"):
                    rcom_shift += obj.get_rcom_pn_shift()
        return (rcom_shift / mtot)

    def get_total_vcom_pn_shift(self):
        """

        """
        mtot = self.get_total_mass()
        vcom_shift = 0.0
        for obj in self.objs:
            if obj.n:
                if hasattr(obj, "get_vcom_pn_shift"):
                    vcom_shift += obj.get_vcom_pn_shift()
        return (vcom_shift / mtot)


    ### linear momentum

    def get_total_lmom_pn_shift(self):
        """

        """
        lmom_shift = 0.0
        for obj in self.objs:
            if obj.n:
                if hasattr(obj, "get_lmom_pn_shift"):
                    lmom_shift += obj.get_lmom_pn_shift()
        return lmom_shift


    ### angular momentum

    def get_total_amom_pn_shift(self):
        """

        """
        amom_shift = 0.0
        for obj in self.objs:
            if obj.n:
                if hasattr(obj, "get_amom_pn_shift"):
                    amom_shift += obj.get_amom_pn_shift()
        return amom_shift


    ### kinetic energy

    def get_total_ke_pn_shift(self):
        """

        """
        ke_shift = 0.0
        for obj in self.objs:
            if obj.n:
                if hasattr(obj, "get_ke_pn_shift"):
                    ke_shift += obj.get_ke_pn_shift()
        return ke_shift


    ### gravity

    def update_pnacc(self, objs, pn_order, clight):
        """
        Update the individual post-newtonian gravitational acceleration due to other particles.
        """
        ni = self.blackhole.n
        nj = objs.blackhole.n
        if ni and nj:
            self.blackhole.update_pnacc(objs.blackhole, pn_order, clight)


########## end of file ##########
