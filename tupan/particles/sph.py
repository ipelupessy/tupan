#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import numpy as np
from .body import Bodies
from ..lib.utils.timing import decallmethods, timings
from ..lib.utils.dtype import *


__all__ = ["Sphs"]


@decallmethods(timings)
class Sphs(Bodies):
    """

    """
    attrs = Bodies.attrs + [
                            ('rho', REAL, "density"),
                           ]
    dtype = [(_[0], _[1]) for _ in attrs]


########## end of file ##########