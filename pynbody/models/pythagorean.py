#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from pynbody.particles import Particles


def make_system(particles_as_type='body', **kwargs):
    _type = particles_as_type
    particles = Particles({_type: 3})
    particles[_type].index[:] = [0, 1, 2]
    particles[_type].mass[:] = [3.0, 4.0, 5.0]
    particles[_type].eps2[:] = [0.0, 0.0, 0.0]
    particles[_type].pos[:] = [
                                [ 1.0,  3.0,  0.0],
                                [-2.0, -1.0,  0.0],
                                [ 1.0, -1.0,  0.0],
                              ]
    particles[_type].vel[:] = [
                                [0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0],
                              ]
    if _type == 'blackhole':
        spin = [
                 [0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0],
               ]
        particles[_type].spin[:] = kwargs.pop("spin", spin)

    particles.set_phi(particles)
    particles.set_acc(particles, 0.0)

    return particles
        

########## end of file ##########