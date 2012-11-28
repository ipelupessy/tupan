#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from ..particles.body import Bodies


def make_system():
    p = Bodies(4)

    p.id = [0, 1, 2, 3]

    p.mass = [1.0, 1.0, 1.0, 1.0]

    p.x = [+1.382857, 0.0,     -1.382857, 0.0     ]
    p.y = [ 0.0,     +0.157030, 0.0,     -0.157030]
    p.z = [ 0.0,      0.0,      0.0,      0.0     ]

    p.vx = [ 0.0,     +1.871935, 0.0,     -1.871935]
    p.vy = [+0.584873, 0.0,     -0.584873, 0.0     ]
    p.vz = [ 0.0,      0.0,      0.0,      0.0     ]

    return p


########## end of file ##########