# -*- coding: utf-8 -*-
#

"""
TODO.
"""


from . import hdf5io
from . import psdfio


class IO(object):
    """

    """
    PROVIDED_FORMATS = ["hdf5", "psdf"]

    def __init__(self, fname, fmode):
        self.fname = fname
        self.fmode = fmode

    def dump_snapshot(self, *args, **kwargs):
        fname = self.fname
        fmode = self.fmode
        if fname.endswith(".psdf"):
            psdfio.PSDFIO(fname, fmode).dump_snapshot(*args, **kwargs)
        elif fname.endswith(".hdf5"):
            hdf5io.HDF5IO(fname, fmode).dump_snapshot(*args, **kwargs)
        else:
            raise NotImplementedError(
                "Unknown format: '{}'. Choose from: {}".format(
                    fname.rpartition('.')[-1], self.PROVIDED_FORMATS
                )
            )

    def load_snapshot(self, *args, **kwargs):
        import os
        import sys
        import logging
        logger = logging.getLogger(__name__)
        from warnings import warn
        fname = self.fname
        fmode = self.fmode
        if not os.path.exists(fname):
            warn("No such file or directory: '{}'".format(fname), stacklevel=2)
            sys.exit()
        loaders = (psdfio.PSDFIO, hdf5io.HDF5IO,)
        for loader in loaders:
            try:
                return loader(fname, fmode).load_snapshot(*args, **kwargs)
            except Exception as exc:
                logger.exception(str(exc))
        raise ValueError("File not in a supported format.")

    def dump_worldline(self, *args, **kwargs):
        fname = self.fname
        fmode = self.fmode
        if fname.endswith(".psdf"):
            psdfio.PSDFIO(fname, fmode).dump_worldline(*args, **kwargs)
        elif fname.endswith(".hdf5"):
            hdf5io.HDF5IO(fname, fmode).dump_worldline(*args, **kwargs)
        else:
            raise NotImplementedError(
                "Unknown format: '{}'. Choose from: {}".format(
                    fname.rpartition('.')[-1], self.PROVIDED_FORMATS
                )
            )

    def load_worldline(self, *args, **kwargs):
        import os
        import sys
        import logging
        logger = logging.getLogger(__name__)
        from warnings import warn
        fname = self.fname
        fmode = self.fmode
        if not os.path.exists(fname):
            warn("No such file or directory: '{}'".format(fname), stacklevel=2)
            sys.exit()
        loaders = (psdfio.PSDFIO, hdf5io.HDF5IO,)
        for loader in loaders:
            try:
                return loader(fname, fmode).load_worldline(*args, **kwargs)
            except Exception as exc:
                logger.exception(str(exc))
        raise ValueError("File not in a supported format.")

    def to_psdf(self):
        fname = self.fname
        fmode = self.fmode
        loaders = (hdf5io.HDF5IO,)
        for loader in loaders:
            try:
                return loader(fname, fmode).to_psdf()
            except Exception:
                pass
        raise ValueError("This file is already in 'psdf' format!")

    def to_hdf5(self):
        fname = self.fname
        fmode = self.fmode
        loaders = (psdfio.PSDFIO,)
        for loader in loaders:
            try:
                return loader(fname, fmode).to_hdf5()
            except Exception:
                pass
        raise ValueError("This file is already in 'hdf5' format!")

    def take_time_slices(self, times):
        import numpy as np
        from scipy import interpolate
        from collections import OrderedDict

        #######################################################################
        import matplotlib.pyplot as plt
        ps0 = IO("snapshots0.hdf5").load_worldline()
        ps1 = IO("snapshots1.hdf5").load_worldline()
        ps = IO("snapshots.hdf5").load_worldline()

        index = ps[ps.nstep == ps.nstep.max()].id[0]
        a0 = ps0[ps0.id == index]
        a1 = ps1[ps1.id == index]
        a = ps[ps.id == index]

        plt.plot(a0.pos[..., 0], a0.pos[..., 1], label="PBaSS: l=1")
        plt.plot(a1.pos[..., 0], a1.pos[..., 1], label="PBaSS: l=8")
        plt.plot(a.pos[..., 0], a.pos[..., 1], label="PBaSS: l=64")
        plt.legend(loc="best", shadow=True,
                   fancybox=True, borderaxespad=0.75)
        plt.show()

        axis = 0
        x = np.linspace(0, 25, 1000000)
        f = interpolate.UnivariateSpline(a1.time, a1.pos[..., axis], s=0, k=2)
        plt.plot(a0.time, a0.pos[..., axis], label="PBaSS: l=1")
        plt.plot(a1.time, a1.pos[..., axis], label="PBaSS: l=8")
        plt.plot(a.time, a.pos[..., axis], label="PBass: l=64")
        plt.plot(x, f(x), label="interp. function")
        plt.legend(loc="best", shadow=True,
                   fancybox=True, borderaxespad=0.75)
        plt.show()
        #######################################################################

        ps = self.load_worldline()

        snaps = OrderedDict()
        for t in times:
            snaps[t] = type(ps)()

        for key, obj in ps.items:
            if obj.n:
                n = int(obj.id.max())+1

                snap = type(obj)(n)
                for t in times:
                    snaps[t].append(snap)

                for i in range(n):
                    stream = obj[obj.id == i]
                    time = stream.time
                    for name in obj.names:
                        attr = getattr(stream, name)
                        if attr.ndim > 1:
                            for k in range(attr.shape[1]):
                                f = interpolate.UnivariateSpline(
                                    time, attr[..., k], s=0, k=2)
                                for t in times:
                                    getattr(getattr(snaps[
                                            t], key), name)[i, k] = f(t)
                        else:
                            f = interpolate.UnivariateSpline(
                                time, attr[...], s=0, k=2)
                            for t in times:
                                getattr(getattr(snaps[t], key), name)[i] = f(t)

        return snaps.values()






########## end of file ##########
