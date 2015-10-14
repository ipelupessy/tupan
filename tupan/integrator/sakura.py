# -*- coding: utf-8 -*-
#

"""
TODO.
"""

import logging
import numpy as np
from .base import Base, power_of_two
from ..lib import extensions as ext
from ..lib.utils.timing import timings, bind_all


LOGGER = logging.getLogger(__name__)


@timings
def sakura_step(ps, dt, kernel=ext.Sakura()):
    """

    """
    ps.pos += ps.vel * dt / 2

    kernel(ps, ps, dt=dt/2, flag=-1)
    ps.pos += ps.dpos
    ps.vel += ps.dvel

    kernel(ps, ps, dt=dt/2, flag=+1)
    ps.pos += ps.dpos
    ps.vel += ps.dvel

    ps.pos += ps.vel * dt / 2

    return ps


@bind_all(timings)
class Sakura(Base):
    """

    """
    PROVIDED_METHODS = ['sakura', 'asakura', ]

    def __init__(self, ps, eta, dt_max, t_begin, method, **kwargs):
        """

        """
        super(Sakura, self).__init__(ps, eta, dt_max,
                                     t_begin, method, **kwargs)

        if 'asakura' in self.method:
            self.update_tstep = True
            self.shared_tstep = True
        else:
            self.update_tstep = False
            self.shared_tstep = True

        self.e0 = None

    def get_sakura_tstep(self, ps, eta, dt):
        """

        """
        ps.set_tstep(ps, eta)

        iw_a = 1 / ps.tstep
        iw_b = 1 / ps.tstepij

        diw = (iw_a - iw_b)

        w_sakura = abs(diw).max()
        w_sakura = np.copysign(w_sakura, eta)
        dt_sakura = 1 / w_sakura

        ps.tstep[...] = dt_sakura

        return power_of_two(ps, dt)

    def do_step(self, ps, dt):
        """

        """
#        p0 = p.copy()
#        if self.e0 is None:
#            self.e0 = p0.kinetic_energy + p0.potential_energy
#        de = [1]
#        tol = dt**2
#        nsteps = 1
#
#        while abs(de[0]) > tol:
#            p = p0.copy()
#            dt = dt / nsteps
#            for i in range(nsteps):
#                p = sakura_step(p, dt)
#                e1 = p.kinetic_energy + p.potential_energy
#                de[0] = e1/self.e0 - 1
#                if abs(de[0]) > tol:
# #                   nsteps += (nsteps+1)//2
#                    nsteps *= 2
# #                   print(nsteps, de, tol)
#                    break

        if self.update_tstep:
            dt = self.get_sakura_tstep(ps, self.eta, dt)
        ps = sakura_step(ps, dt)

        ps.tstep[...] = dt
        ps.time += dt
        ps.nstep += 1
        type(ps).t_curr += dt
        return ps


# -- End of File --
