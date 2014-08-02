# -*- coding: utf-8 -*-
#

"""This module implements highlevel interfaces for C/CL-extensions.

"""


from __future__ import print_function, division
import logging
from ..config import options
from .utils.timing import timings, bind_all


__all__ = ['Phi', 'Acc', 'AccJerk', 'SnapCrackle', 'Tstep',
           'PNAcc', 'Sakura', 'NregX', 'NregV', 'Kepler', ]

LOGGER = logging.getLogger(__name__)


@bind_all(timings)
class PN(object):
    """This class holds the values of the PN parameters.

    """
    def __init__(self):
        self._order = 0
        self._clight = None

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = int(value)

    @property
    def clight(self):
        return self._clight

    @clight.setter
    def clight(self, value):
        self._clight = float(value)


class AbstractExtension(object):
    """

    """
    def __init__(self, name, backend):
        if backend == 'C':
            from .backend_cffi import drv
        elif backend == 'CL':
            from .backend_opencl import drv
        else:
            msg = "backend: invalid choice: '{}' (choose from 'C', 'CL')"
            raise ValueError(msg.format(backend))
        self.kernel = drv.get_kernel(name)

    def set_args(self, ips, jps, **kwargs):
        raise NotImplementedError

    def run(self):
        self.kernel.run()

    def get_result(self):
        return self.kernel.map_buffers()

    def __call__(self, ips, jps, **kwargs):
        self.set_args(ips, jps, **kwargs)
        self.run()
        return self.get_result()


@bind_all(timings)
class Phi(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Phi, self).__init__('phi_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2)

        outargs = (ips.phi,)

        self.kernel.set_args(inpargs, outargs)

    def _pycalc(self, ips, jps):
        # Never use this method for production runs. It is very slow
        # and it's here only for performance comparisons. It is also
        # likely that only the classes Acc and Phi will have an
        # implementation of this method.
        import numpy as np
        for i in range(ips.n):
            rx = ips.rx[i] - jps.rx
            ry = ips.ry[i] - jps.ry
            rz = ips.rz[i] - jps.rz
            e2 = ips.eps2[i] + jps.eps2
            r2 = rx * rx + ry * ry + rz * rz
            mask = r2 > 0
            inv_r2 = 1 / (r2 + e2)
            inv_r = np.sqrt(inv_r2)
            ips.phi[i] = -(jps.mass * inv_r)[mask].sum()
        return (ips.phi,)
#    calc = _pycalc


@bind_all(timings)
class Acc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Acc, self).__init__('acc_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2)

        outargs = (ips.ax, ips.ay, ips.az)

        self.kernel.set_args(inpargs, outargs)

    def _pycalc(self, ips, jps):
        # Never use this method for production runs. It is very slow
        # and it's here only for performance comparisons. It is also
        # likely that only the classes Acc and Phi will have an
        # implementation of this method.
        import numpy as np
        for i in range(ips.n):
            rx = ips.rx[i] - jps.rx
            ry = ips.ry[i] - jps.ry
            rz = ips.rz[i] - jps.rz
            e2 = ips.eps2[i] + jps.eps2
            r2 = rx * rx + ry * ry + rz * rz
            mask = r2 > 0
            inv_r2 = 1 / (r2 + e2)
            inv_r = np.sqrt(inv_r2)
            inv_r3 = inv_r * inv_r2
            inv_r3 *= jps.mass
            ips.ax[i] = -(inv_r3 * rx)[mask].sum()
            ips.ay[i] = -(inv_r3 * ry)[mask].sum()
            ips.az[i] = -(inv_r3 * rz)[mask].sum()
        return (ips.ax, ips.ay, ips.az)
#    calc = _pycalc


@bind_all(timings)
class AccJerk(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(AccJerk, self).__init__('acc_jerk_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz)

        outargs = (ips.ax, ips.ay, ips.az,
                   ips.jx, ips.jy, ips.jz)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class SnapCrackle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(SnapCrackle, self).__init__('snap_crackle_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   ips.ax, ips.ay, ips.az, ips.jx, ips.jy, ips.jz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   jps.ax, jps.ay, jps.az, jps.jx, jps.jy, jps.jz)

        outargs = (ips.sx, ips.sy, ips.sz,
                   ips.cx, ips.cy, ips.cz)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Tstep(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Tstep, self).__init__('tstep_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   kwargs['eta'])

        outargs = (ips.tstep, ips.tstepij)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class PNAcc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(PNAcc, self).__init__('pnacc_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   pn.order, pn.clight**(-1),
                   pn.clight**(-2), pn.clight**(-3),
                   pn.clight**(-4), pn.clight**(-5),
                   pn.clight**(-6), pn.clight**(-7))

        outargs = (ips.pnax, ips.pnay, ips.pnaz)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Sakura(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Sakura, self).__init__('sakura_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'drx'):
            ips.register_attribute('drx', 'real')
        if not hasattr(ips, 'dry'):
            ips.register_attribute('dry', 'real')
        if not hasattr(ips, 'drz'):
            ips.register_attribute('drz', 'real')
        if not hasattr(ips, 'dvx'):
            ips.register_attribute('dvx', 'real')
        if not hasattr(ips, 'dvy'):
            ips.register_attribute('dvy', 'real')
        if not hasattr(ips, 'dvz'):
            ips.register_attribute('dvz', 'real')

        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   kwargs['dt'], kwargs['flag'])

        outargs = (ips.drx, ips.dry, ips.drz,
                   ips.dvx, ips.dvy, ips.dvz)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class NregX(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(NregX, self).__init__('nreg_Xkernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mrx'):
            ips.register_attribute('mrx', 'real')
        if not hasattr(ips, 'mry'):
            ips.register_attribute('mry', 'real')
        if not hasattr(ips, 'mrz'):
            ips.register_attribute('mrz', 'real')
        if not hasattr(ips, 'ax'):
            ips.register_attribute('ax', 'real')
        if not hasattr(ips, 'ay'):
            ips.register_attribute('ay', 'real')
        if not hasattr(ips, 'az'):
            ips.register_attribute('az', 'real')
        if not hasattr(ips, 'u'):
            ips.register_attribute('u', 'real')

        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   kwargs['dt'])

        outargs = (ips.mrx, ips.mry, ips.mrz,
                   ips.ax, ips.ay, ips.az,
                   ips.u)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class NregV(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(NregV, self).__init__('nreg_Vkernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mvx'):
            ips.register_attribute('mvx', 'real')
        if not hasattr(ips, 'mvy'):
            ips.register_attribute('mvy', 'real')
        if not hasattr(ips, 'mvz'):
            ips.register_attribute('mvz', 'real')
        if not hasattr(ips, 'mk'):
            ips.register_attribute('mk', 'real')

        inpargs = (ips.n,
                   ips.mass, ips.vx, ips.vy, ips.vz,
                   ips.ax, ips.ay, ips.az,
                   jps.n,
                   jps.mass, jps.vx, jps.vy, jps.vz,
                   jps.ax, jps.ay, jps.az,
                   kwargs['dt'])

        outargs = (ips.mvx, ips.mvy, ips.mvz, ips.mk)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Kepler(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):

        if backend == 'CL':    # No need for CL support.
            backend = 'C'      # C is fast enough!

        super(Kepler, self).__init__('kepler_solver_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rx, ips.ry, ips.rz,
                   ips.eps2, ips.vx, ips.vy, ips.vz,
                   jps.n,
                   jps.mass, jps.rx, jps.ry, jps.rz,
                   jps.eps2, jps.vx, jps.vy, jps.vz,
                   kwargs['dt'])

        outargs = (ips.rx, ips.ry, ips.rz,
                   ips.vx, ips.vy, ips.vz)

        self.kernel.set_args(inpargs, outargs)


pn = PN()


# -- End of File --
