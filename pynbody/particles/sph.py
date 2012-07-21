#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import numpy as np
from .pbase import Pbase, with_properties
from ..lib.utils.timing import decallmethods, timings


__all__ = ['Sph']


@decallmethods(timings)
@with_properties
class Sph(Pbase):
    """
    A base class for Sph.
    """
    #--format--:  (name, type, doc)
    attributes = [# common attributes
                  ('id', 'u8', 'index'),
                  ('mass', 'f8', 'mass'),
                  ('pos', '3f8', 'position'),
                  ('vel', '3f8', 'velocity'),
                  ('acc', '3f8', 'acceleration'),
                  ('phi', 'f8', 'potential'),
                  ('eps2', 'f8', 'softening'),
                  ('t_curr', 'f8', 'current time'),
                  ('dt_prev', 'f8', 'previous time-step'),
                  ('dt_next', 'f8', 'next time-step'),
                  ('nstep', 'u8', 'step number'),
                  # specific attributes

                  # auxiliary attributes

                 ]

    attrs = ["id", "mass", "pos", "vel", "acc", "phi", "eps2",
             "t_curr", "dt_prev", "dt_next", "nstep"]

    dtype = [(_[0], _[1]) for _ in attributes]

    zero = np.zeros(0, dtype)


    #
    # specific methods
    #

    ### ...


    #
    # auxiliary methods
    #

    ### ...


    #
    # overridden methods
    #

    ### ...


########## end of file ##########
