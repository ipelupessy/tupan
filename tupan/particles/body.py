# -*- coding: utf-8 -*-
#

"""
TODO.
"""


from .base import Particle
from ..lib.utils.timing import timings, bind_all


__all__ = ['Bodies']


@bind_all(timings)
class Bodies(Particle):
    """

    """
    name = None
    default_attr_descr = Particle.default_attr_descr + []


# -- End of File --
