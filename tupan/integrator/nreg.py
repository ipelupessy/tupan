# -*- coding: utf-8 -*-
#

"""This module implements the N-body formulation of the algorithmic
regularization procedure by Mikkola & Tanikawa, MNRAS, 310, 745-749 (1999).
"""

from .base import Base


def drift(ps, h):
    """

    """
    W = ps.kinetic_energy + ps.B
    dt = h / W
    for p in ps.members.values():
        if p.n:
            p.time += dt
            p.rdot[0] += p.rdot[1] * dt
    return ps, W


def kick(ps, h):
    """

    """
    ps.set_acc(ps)
    ps.set_phi(ps)
    U = -ps.potential_energy
    dt = h / U
    for p in ps.members.values():
        if p.n:
            p.rdot[1] += p.rdot[2] * dt
    return ps, U


def a_nreg_step(ps, h):
    """

    """
    ps, _ = drift(ps, h/2)
    ps, _ = kick(ps, h)
    ps, _ = drift(ps, h/2)

    for p in ps.members.values():
        if p.n:
            p.nstep += 1
    return ps


def c_nreg_step(ps, h):
    """

    """
    try:
        U = ps.U
    except:
        ps.set_phi(ps)
        U = -ps.potential_energy
        ps.U = U

    ps, _ = drift(ps, U * h/2)
    ps, _ = kick(ps, U * h)
    ps, W = drift(ps, U * h/2)
    ps.U = U = (W**2) / ps.U

    for p in ps.members.values():
        if p.n:
            p.nstep += 1
    return ps


class NREG(Base):
    """

    """
    PROVIDED_METHODS = [
        'c.nreg', 'a.nreg',
    ]

    def __init__(self, ps, cli, *args, **kwargs):
        """

        """
        super(NREG, self).__init__(ps, cli, *args, **kwargs)

        self.update_tstep = False
        self.shared_tstep = True

        ps.set_phi(ps)
        T = ps.kinetic_energy
        U = -ps.potential_energy
        ps.B = U - T

    def do_step(self, ps, h):
        """

        """
        if 'c.' in self.cli.method:
            return c_nreg_step(ps, h)
        elif 'a.' in self.cli.method:
            return a_nreg_step(ps, h)
        else:
            raise NotImplemented(self.cli.method)


# -- End of File --
