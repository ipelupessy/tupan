#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import numpy as np

from ggf84decor import selftimer


__all__ = ["LeapFrog"]



_coefs = [1.0]

#_coefs = [1.3512071919596575,
#         -1.7024143839193150,
#          1.3512071919596575]

#_coefs = [0.4144907717943757,
#          0.4144907717943757,
#         -0.6579630871775028,
#          0.4144907717943757,
#          0.4144907717943757]

#_coefs = [0.3221375960817983,
#          0.5413165481700432,
#         -0.7269082885036829,
#          0.5413165481700432,
#          0.3221375960817983]

#_coefs = [0.7845136104775573,
#          0.23557321335935813,
#         -1.177679984178871,
#          1.3151863206839112,
#         -1.177679984178871,
#          0.23557321335935813,
#          0.7845136104775573]

#_coefs = [0.1867,
#          0.5554970237124784,
#          0.12946694891347535,
#         -0.8432656233877346,
#          0.9432033015235617,
#         -0.8432656233877346,
#          0.12946694891347535,
#          0.5554970237124784,
#          0.1867]


class LeapFrog(object):
    """

    """
    def __init__(self, eta, time, particles, coefs=_coefs):
        self.eta = eta
        self.time = time
        self.coefs = coefs
        particles.set_phi(particles)
        rhostep = particles.set_acc(particles)
        self.particles = particles
        self.e0 = self.particles.get_total_energies()

        self.dvel = {}
#        varstep = 1.0
        varstep = 0.5 / (-self.e0.pot)
        for (key, obj) in self.particles.iteritems():
            if hasattr(obj, "_pnacc"):
                self.dvel[key] = varstep * (obj.acc + obj._pnacc)
            elif obj:
                self.dvel[key] = varstep * obj.acc



    @selftimer
    def gather(self):
        return self.particles


    @selftimer
    def drift(self, stepcoef):
        """

        """
        e = self.particles.get_total_energies()
#        varstep = 1.0
        varstep = 0.5 / (e.kin - self.e0.tot)
        tau = 0.5 * stepcoef * self.eta
        self.time += tau * varstep
        for (key, obj) in self.particles.iteritems():
            if obj:
                obj.drift(tau * varstep)
                if hasattr(obj, "_rcomjump"):
                    obj._rcomjump += tau * varstep * obj._vcomjump


    @selftimer
    def kick(self, stepcoef):
        """

        """
        tau = 0.5 * stepcoef * self.eta
        for (key, obj) in self.particles.iteritems():
            if obj:
                obj.kick(tau * self.dvel[key])


    @selftimer
    def forceDKD(self, jparticles, stepcoef):
        """

        """
        rhostep = self.particles.set_acc(jparticles)
        self.particles.set_phi(jparticles)

        e = self.particles.get_total_energies()
#        varstep = 1.0
        varstep = 0.5 / (-e.pot)
        tau = stepcoef * self.eta
        for (key, obj) in self.particles.iteritems():
            if obj:
                g0 = self.dvel[key].copy()
                if hasattr(obj, "_pnacc"):
                    _acc = (obj.acc + obj._pnacc)
                else:
                    _acc = obj.acc
                self.dvel[key] = 2 * varstep * _acc - self.dvel[key]
                g1 = self.dvel[key].copy()
                force_ext = (obj.mass * (obj.acc - _acc).T).T
                if hasattr(obj, "_ejump"):
                    v12 = obj.vel + 0.25 * tau * (g1-g0)
                    ejump = (v12 * force_ext).sum(1)
                    obj._ejump += tau * varstep * ejump
                if hasattr(obj, "_vcomjump"):
                    vcomjump = force_ext.sum(0) / obj.get_total_mass()
                    obj._vcomjump += tau * varstep * vcomjump
                if hasattr(obj, "_linmomjump"):
                    linmomjump = force_ext
                    obj._linmomjump += tau * varstep * linmomjump
                if hasattr(obj, "_angmomjump"):
                    angmomjump = np.cross(obj.pos, force_ext)
                    obj._angmomjump += tau * varstep * angmomjump


    def stepDKD(self, stepcoef):
        """

        """
        self.drift(stepcoef)
        self.kick(stepcoef)
        self.forceDKD(self.gather(), stepcoef)
        self.kick(stepcoef)
        self.drift(stepcoef)


    @selftimer
    def step(self):
        """

        """
        ncoefs = len(self.coefs)
        for coef in self.coefs:
            self.stepDKD(ncoefs*coef)







########## end of file ##########
