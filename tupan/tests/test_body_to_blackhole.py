#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

if __name__ == "__main__":
    from tupan.ics.imf import IMF
    from tupan.ics.plummer import Plummer
    from tupan.particles import System
    from tupan.io import IO
    import matplotlib.pyplot as plt
    import numpy as np

    numBodies = 256

    def main():

#        imf = IMF.equal()
#        imf = IMF.salpeter1955(0.5, 120.0)
#        imf = IMF.parravano2011(0.075, 120.0)
        imf = IMF.padoan2007(0.075, 120.0)

        p = Plummer(numBodies, imf, eps=4.0/numBodies, eps_parametrization=0, seed=1)
        p.make_plummer()

        fname = "plummer"+str(numBodies).zfill(4)+".hdf5"
        io = IO(fname, 'w')
        io.dump_snapshot(p.particles)

#        p.show()

        return p.particles.copy()


    p = main()

    from tupan.ics import *
    from tupan.particles.blackhole import Blackholes
    bh = figure8.make_system().astype(Blackholes)
    p.append(bh)

    fname = "plummer"+str(numBodies).zfill(4)+'-'+"3bh"+".hdf5"
    io = IO(fname, 'w')
    io.dump_snapshot(p)


########## end of file ##########