# -*- coding: utf-8 -*-
#

"""
TODO.
"""


from __future__ import (print_function, division)
import logging
import numpy as np
from ..particles.allparticles import ParticleSystem
from ..lib.utils.timing import decallmethods, timings


__all__ = ['Plummer']

logger = logging.getLogger(__name__)


@decallmethods(timings)
class Plummer(object):
    """  """

    def __init__(self, n, eps, imf, seed=None, mfrac=0.999, softening_type=0):
        self.n = n
        self.eps2 = eps*eps
        self.imf = imf
        self.mfrac = mfrac
        self.softening_type = softening_type
        self.ps = ParticleSystem(n)
        np.random.seed(seed)

    def set_eps2(self, mass):
        n = self.n
        if self.softening_type == 0:
            # eps2 ~ cte
            eps2 = np.ones(n)
        elif self.softening_type == 1:
            # eps2 ~ m^2 ~ 1/n^2 if m ~ 1/n
            eps2 = mass**2
        elif self.softening_type == 2:
            # eps2 ~ m/n ~ 1/n^2 if m ~ 1/n
            eps2 = mass / n
        elif self.softening_type == 3:
            # eps2 ~ (m/n^2)^(2/3) ~ 1/n^2 if m ~ 1/n
            eps2 = (mass / n**2)**(2.0/3)
        elif self.softening_type == 4:
            # eps2 ~ (1/(m*n^2))^2 ~ 1/n^2 if m ~ 1/n
            eps2 = (1.0 / (mass * n**2))**2
        else:
            logger.critical(
                "Unexpected value for softening_type: %d.",
                self.softening_type)
            raise ValueError(
                "Unexpected value for softening_type: {}.".format(
                    self.softening_type))

        # normalizes by the provided scale of eps2
        eps2 *= self.eps2 / np.mean(eps2)

        # return half of real value in order to avoid to do this in force loop.
        return eps2 / 2

    def set_pos(self, irand):
        n = self.n
        mfrac = self.mfrac
        mrand = (irand + np.random.random(n)) * mfrac / n
        radius = 1.0 / np.sqrt(np.power(mrand, -2.0 / 3.0) - 1.0)
        theta = np.arccos(np.random.uniform(-1.0, 1.0, size=n))
        phi = np.random.uniform(0.0, 2.0 * np.pi, size=n)
        rx = radius * np.sin(theta) * np.cos(phi)
        ry = radius * np.sin(theta) * np.sin(phi)
        rz = radius * np.cos(theta)
        return (rx, ry, rz)

    def set_vel(self, pot):
        count = 0
        n = self.n
        rnd = np.empty(n)
        while count < n:
            r1 = np.random.random()
            r2 = np.random.random()
            if (r2 < r1):
                rnd[count] = r2
                count += 1
        velocity = np.sqrt(-2 * rnd * pot)
        theta = np.arccos(np.random.uniform(-1.0, 1.0, size=n))
        phi = np.random.uniform(0.0, 2.0 * np.pi, size=n)
        vx = velocity * np.sin(theta) * np.cos(phi)
        vy = velocity * np.sin(theta) * np.sin(phi)
        vz = velocity * np.cos(theta)
        return (vx, vy, vz)

    def set_bodies(self):
        """  """
        n = self.n
        ilist = np.arange(n)

        # set index
        self.ps.id[...] = ilist

        srand = np.random.get_state()

        # set mass
        self.ps.mass[...] = self.imf.sample(n)
        self.ps.mass /= self.ps.total_mass

        # set eps2
        self.ps.eps2[...] = self.set_eps2(self.ps.mass)

        np.random.set_state(srand)

        # set pos
        pos = self.set_pos(np.random.permutation(ilist))
        self.ps.rx[...] = pos[0]
        self.ps.ry[...] = pos[1]
        self.ps.rz[...] = pos[2]

        # set phi
        self.ps.set_phi(self.ps)

        # set vel
        vel = self.set_vel(self.ps.phi)
        self.ps.vx[...] = vel[0]
        self.ps.vy[...] = vel[1]
        self.ps.vz[...] = vel[2]

    def make_model(self):
        self.set_bodies()
        self.ps.com_to_origin()
        self.ps.to_nbody_units()
        self.ps.scale_to_virial()

    def show(self, nbins=32):
        from scipy import optimize
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle

        mass = self.imf._mtot * self.ps.mass.copy()

        ###################################

        (hist, bins) = np.histogram(np.log10(mass), bins=nbins)
        linbins = np.power(10.0, bins)
        selection = np.where(hist > 0)

        fitfunc = lambda k, m: k * self.imf.func(m)
        errfunc = lambda k, m, y: fitfunc(k, m)[selection] - y[selection]
        k0 = 1.0
        k1, success = optimize.leastsq(errfunc, k0, args=(linbins[:-1], hist))
        x = np.logspace(np.log10(self.imf.min_mlow),
                        np.log10(self.imf.max_mhigh),
                        num=128, base=10.0)
        y = fitfunc(k1, x)

        ###################################
        # IMF plot

        fig = plt.figure(figsize=(13.5, 6))
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.plot(bins[selection], np.log10(hist[selection]),
                 'bo', label='IMF sample')
        ax1.plot(np.log10(x), np.log10(y), 'r--',
                 label='IMF distribution', linewidth=1.5)
        ax1.grid(True)
        ax1.set_xlabel(r'$\log_{10}(m)$', fontsize=18)
        ax1.set_ylabel(r'$\log_{10}(dN/d\log_{10}(m))$', fontsize=18)
        ax1.legend(loc='lower left', shadow=True,
                   fancybox=True, borderaxespad=0.75)

        ###################################

        b = self.ps
        n = b.n
        rx = b.rx
        ry = b.ry
        radius = 2 * n * b.mass
        color = n * b.mass

        ###################################
        # Scatter plot

        ax2 = fig.add_subplot(1, 2, 2)
#        ax.set_axis_bgcolor('0.75')
        ax2.scatter(rx, ry, c=color, s=radius, cmap='gist_rainbow',
                    alpha=0.75, label=r'$Stars$')
        circle = Circle(
            (0, 0), 1,
            facecolor='none',
            edgecolor=(1, 0.25, 0),
            linewidth=1.5,
            label=r'$R_{Vir}$'
        )
        ax2.add_patch(circle)

        ax2.set_xlim(-4, +4)
        ax2.set_ylim(-4, +4)

        ax2.set_xlabel(r'$x$', fontsize=18)
        ax2.set_ylabel(r'$y$', fontsize=18)
        ax2.legend(loc='upper right', shadow=True,
                   fancybox=True, borderaxespad=0.75)

        ###################################
        # Show
        plt.savefig('show.png', bbox_inches="tight")
#        plt.savefig('show.pdf', bbox_inches="tight")
        plt.show()
        plt.close()


def make_plummer(n, eps, imf, seed=None, mfrac=0.999, softening_type=0):
    if n < 2:
        n = 2
    from tupan.ics.imf import IMF
    imf = getattr(IMF, imf[0])(*imf[1:])
    p = Plummer(n, eps, imf, seed=seed, mfrac=mfrac,
                softening_type=softening_type)
    p.make_model()
    return p.ps


########## end of file ##########
