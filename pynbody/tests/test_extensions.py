#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test suite for extensions module.
"""


from __future__ import print_function
import sys
import numpy as np
import unittest
from pynbody.lib import extensions
from pynbody.lib.extensions import NewExtensions
from pynbody.lib.utils.timing import (Timer, timings)



print('setup: ...')
cext32 = NewExtensions(dtype='f', junroll=8)
cext64 = NewExtensions(dtype='d', junroll=8)
clext32 = NewExtensions(dtype='f', junroll=8)
clext64 = NewExtensions(dtype='d', junroll=8)
cext32.build_kernels(device='cpu')
cext64.build_kernels(device='cpu')
clext32.build_kernels(device='gpu')
clext64.build_kernels(device='gpu')
def set_particles(npart):
    if npart < 2: npart = 2
    from pynbody.models.imf import IMF
    from pynbody.models.plummer import Plummer
    imf = IMF.padoan2007(0.075, 120.0)
    p = Plummer(npart, imf, epsf=0.0, epstype='b', seed=1)
    p.make_plummer()
    bi = p.particles['body']
    return bi
small_system = set_particles(64)
large_system = set_particles(8192)



class TestCase(unittest.TestCase):


    def test1(self):
        print('\ntest1: mean gravitational phi deviation (single precision on CPU and GPU):', end=' ')

        phi = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        data = (iposmass, iobj.eps2,
                jposmass, jobj.eps2,
                np.uint32(ni),
                np.uint32(nj))

        output_buf = np.empty(ni)
        lmem_layout = (4, 1)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        phi_kernel = cext32.get_kernel("p2p_phi_kernel")
        phi_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        phi_kernel.run()
        phi['cpu_result'] = phi_kernel.get_result()


        # calculating on GPU
        phi_kernel = clext32.get_kernel("p2p_phi_kernel")
        phi_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        phi_kernel.run()
        phi['gpu_result'] = phi_kernel.get_result()

        # calculating diff of result
        phi_deviation = np.abs(phi['cpu_result'] - phi['gpu_result'])
        print(phi_deviation.mean())



    def test2(self):
        print('\ntest2: mean gravitational phi deviation (double precision on CPU and GPU):', end=' ')

        phi = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        data = (iposmass, iobj.eps2,
                jposmass, jobj.eps2,
                np.uint32(ni),
                np.uint32(nj))

        output_buf = np.empty(ni)
        lmem_layout = (4, 1)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        phi_kernel = cext64.get_kernel("p2p_phi_kernel")
        phi_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        phi_kernel.run()
        phi['cpu_result'] = phi_kernel.get_result()


        # calculating on GPU
        phi_kernel = clext64.get_kernel("p2p_phi_kernel")
        phi_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        phi_kernel.run()
        phi['gpu_result'] = phi_kernel.get_result()

        # calculating diff of result
        phi_deviation = np.abs(phi['cpu_result'] - phi['gpu_result'])
        print(phi_deviation.mean())


    def test3(self):
        print('\ntest3: mean gravitational acc deviation (single precision on CPU and GPU):', end=' ')

        acc = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        iveleps2 = np.vstack((iobj.vel.T, iobj.eps2)).T
        jveleps2 = np.vstack((jobj.vel.T, jobj.eps2)).T
        data = (iposmass, iveleps2,
                jposmass, jveleps2,
                np.uint32(ni),
                np.uint32(nj),
                np.float64(0.0))

        output_buf = np.empty((ni,4))
        lmem_layout = (4, 4)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        acc_kernel = cext32.get_kernel("p2p_acc_kernel")
        acc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        acc_kernel.run()
        acc['cpu_result'] = acc_kernel.get_result()[:,:3]


        # calculating on GPU
        acc_kernel = clext32.get_kernel("p2p_acc_kernel")
        acc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        acc_kernel.run()
        acc['gpu_result'] = acc_kernel.get_result()[:,:3]

        # calculating diff of result
        acc_deviation = np.abs(  np.sqrt((acc['cpu_result']**2).sum(1))
                               - np.sqrt((acc['gpu_result']**2).sum(1)))
        print(acc_deviation.mean())


    def test4(self):
        print('\ntest4: mean gravitational acc deviation (double precision on CPU and GPU):', end=' ')

        acc = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        iveleps2 = np.vstack((iobj.vel.T, iobj.eps2)).T
        jveleps2 = np.vstack((jobj.vel.T, jobj.eps2)).T
        data = (iposmass, iveleps2,
                jposmass, jveleps2,
                np.uint32(ni),
                np.uint32(nj),
                np.float64(0.0))

        output_buf = np.empty((ni,4))
        lmem_layout = (4, 4)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        acc_kernel = cext64.get_kernel("p2p_acc_kernel")
        acc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        acc_kernel.run()
        acc['cpu_result'] = acc_kernel.get_result()[:,:3]


        # calculating on GPU
        acc_kernel = clext64.get_kernel("p2p_acc_kernel")
        acc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        acc_kernel.run()
        acc['gpu_result'] = acc_kernel.get_result()[:,:3]

        # calculating diff of result
        acc_deviation = np.abs(  np.sqrt((acc['cpu_result']**2).sum(1))
                               - np.sqrt((acc['gpu_result']**2).sum(1)))
        print(acc_deviation.mean())


    def test5(self):
        print('\ntest5: mean gravitational pnacc deviation (single precision on CPU and GPU):', end=' ')

        pnacc = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        iveliv2 = np.vstack((iobj.vel.T, (iobj.vel**2).sum(1))).T
        jveljv2 = np.vstack((jobj.vel.T, (jobj.vel**2).sum(1))).T
        from pynbody.lib.gravity import Clight
        clight = Clight(7, 128)
        data = (iposmass, iveliv2,
                jposmass, jveljv2,
                np.uint32(ni),
                np.uint32(nj),
                np.uint32(clight.pn_order), np.float64(clight.inv1),
                np.float64(clight.inv2), np.float64(clight.inv3),
                np.float64(clight.inv4), np.float64(clight.inv5),
                np.float64(clight.inv6), np.float64(clight.inv7),
               )

        output_buf = np.empty((ni,4))
        lmem_layout = (4, 4)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        pnacc_kernel = cext32.get_kernel("p2p_pnacc_kernel")
        pnacc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        pnacc_kernel.run()
        pnacc['cpu_result'] = pnacc_kernel.get_result()[:,:3]


        # calculating on GPU
        pnacc_kernel = clext32.get_kernel("p2p_pnacc_kernel")
        pnacc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        pnacc_kernel.run()
        pnacc['gpu_result'] = pnacc_kernel.get_result()[:,:3]

        # calculating diff of result
        pnacc_deviation = np.abs(  np.sqrt((pnacc['cpu_result']**2).sum(1))
                                 - np.sqrt((pnacc['gpu_result']**2).sum(1)))
        print(pnacc_deviation.mean())


    def test6(self):
        print('\ntest6: mean gravitational pnacc deviation (double precision on CPU and GPU):', end=' ')

        pnacc = {'cpu_result': None, 'gpu_result': None}

        # setup data
        iobj = small_system.copy()
        jobj = small_system.copy()
        ni = len(iobj)
        nj = len(jobj)
        iposmass = np.vstack((iobj.pos.T, iobj.mass)).T
        jposmass = np.vstack((jobj.pos.T, jobj.mass)).T
        iveliv2 = np.vstack((iobj.vel.T, (iobj.vel**2).sum(1))).T
        jveljv2 = np.vstack((jobj.vel.T, (jobj.vel**2).sum(1))).T
        from pynbody.lib.gravity import Clight
        clight = Clight(7, 128)
        data = (iposmass, iveliv2,
                jposmass, jveljv2,
                np.uint32(ni),
                np.uint32(nj),
                np.uint32(clight.pn_order), np.float64(clight.inv1),
                np.float64(clight.inv2), np.float64(clight.inv3),
                np.float64(clight.inv4), np.float64(clight.inv5),
                np.float64(clight.inv6), np.float64(clight.inv7),
               )

        output_buf = np.empty((ni,4))
        lmem_layout = (4, 4)
        local_size = 384
        global_size = ((ni-1)//local_size + 1) * local_size


        # calculating on CPU
        pnacc_kernel = cext64.get_kernel("p2p_pnacc_kernel")
        pnacc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        pnacc_kernel.run()
        pnacc['cpu_result'] = pnacc_kernel.get_result()[:,:3]


        # calculating on GPU
        pnacc_kernel = clext64.get_kernel("p2p_pnacc_kernel")
        pnacc_kernel.set_kernel_args(*data, global_size=global_size,
                                          local_size=local_size,
                                          output_buf=output_buf,
                                          lmem_layout=lmem_layout)
        pnacc_kernel.run()
        pnacc['gpu_result'] = pnacc_kernel.get_result()[:,:3]

        # calculating diff of result
        pnacc_deviation = np.abs(  np.sqrt((pnacc['cpu_result']**2).sum(1))
                                 - np.sqrt((pnacc['gpu_result']**2).sum(1)))
        print(pnacc_deviation.mean())


    def test7(self):
        print('\ntest7: stupid test')































def run_all():
    kernels = extensions.ALL_KERNELS
    compare_ret_C_vs_CL(kernels)
    performance_C_vs_CL(kernels)


##############################################

#    from pynbody.io import HDF5IO
#    ic = HDF5IO("plummer0000b-3bh")
#    p = ic.read_snapshot()
#    p.set_acc(p)
#    bi = p['blackhole']
#    print(bi._pnacc)

#    pnacc = test_pnacc(kernels["c_lib64_p2p_pnacc_kernel"], bi, bi.copy())

#    print(pnacc[:,:3])

##############################################



def compare_ret_C_vs_CL(kernels):
    bi = set_particles(64)
    compare(test_phi, kernels["c_lib64_p2p_phi_kernel"],
                      kernels["cl_lib64_p2p_phi_kernel"], bi)
    compare(test_acc, kernels["c_lib64_p2p_acc_kernel"],
                      kernels["cl_lib64_p2p_acc_kernel"], bi)


def performance_C_vs_CL(kernels):
    bi = set_particles(8192)
    bj = bi.copy()

    # -------------------------------------------

    ni = len(bi)
    nj = len(bj)
    iposmass = np.vstack((bi.pos.T, bi.mass)).T
    jposmass = np.vstack((bj.pos.T, bj.mass)).T
    phi_data = (iposmass, bi.eps2,
                jposmass, bj.eps2,
                np.uint32(ni),
                np.uint32(nj))

    iposmass = np.vstack((bi.pos.T, bi.mass)).T
    jposmass = np.vstack((bj.pos.T, bj.mass)).T
    iveleps2 = np.vstack((bi.vel.T, bi.eps2)).T
    jveleps2 = np.vstack((bj.vel.T, bj.eps2)).T
    acc_data = (iposmass, iveleps2,
                jposmass, jveleps2,
                np.uint32(ni),
                np.uint32(nj),
                np.float64(0.0))

    # -------------------------------------------

    print("\n\nDouble Precision Performance:")
    print("-----------------------------")
    performance_test(kernels["c_lib64_p2p_phi_kernel"],
                     kernels["cl_lib64_p2p_phi_kernel"], ni, nj, phi_data,
                     output_shape="({ni},)", lmem_layout=(4, 1))
    performance_test(kernels["c_lib64_p2p_acc_kernel"],
                     kernels["cl_lib64_p2p_acc_kernel"], ni, nj, acc_data,
                     output_shape="({ni},4)", lmem_layout=(4, 4))
    print("\n\nSingle Precision Performance:")
    print("-----------------------------")
    performance_test(kernels["c_lib32_p2p_phi_kernel"],
                     kernels["cl_lib32_p2p_phi_kernel"], ni, nj, phi_data,
                     output_shape="({ni},)", lmem_layout=(4, 1))
    performance_test(kernels["c_lib32_p2p_acc_kernel"],
                     kernels["cl_lib32_p2p_acc_kernel"], ni, nj, acc_data,
                     output_shape="({ni},4)", lmem_layout=(4, 4))




def set_particles(npart):
    if npart < 2: npart = 2
    from pynbody.models.imf import IMF
    from pynbody.models.plummer import Plummer
    imf = IMF.padoan2007(0.075, 120.0)
    p = Plummer(npart, imf, epsf=0.0, epstype='b', seed=1)
    p.make_plummer()
    bi = p.particles['body']
    return bi




def test_phi(cext, clext, bi, bj):
    # -------------------------------------------

    ni = len(bi)
    nj = len(bj)
    iposmass = np.vstack((bi.pos.T, bi.mass)).T
    jposmass = np.vstack((bj.pos.T, bj.mass)).T
    data = (iposmass, bi.eps2,
            jposmass, bj.eps2,
            np.uint32(ni),
            np.uint32(nj))

    output_buf = np.empty_like(bi.phi)
    lmem_layout = (4, 1)

    # Adjusts global_size to be an integer multiple of local_size
    local_size = 384
    global_size = ((ni-1)//local_size + 1) * local_size

    # -------------------------------------------

    # XXX: kw has no efects with C extensions!
    cext.set_kernel_args(*data, global_size=global_size,
                                local_size=local_size,
                                output_buf=output_buf,
                                lmem_layout=lmem_layout)
    cext.run()
    cres = cext.get_result()
    cepot = 0.5 * np.sum(bi.mass * cres)

    # -------------------------------------------

    clext.set_kernel_args(*data, global_size=global_size,
                                 local_size=local_size,
                                 output_buf=output_buf,
                                 lmem_layout=lmem_layout)
    clext.run()
    clres = clext.get_result()
    clepot = 0.5 * np.sum(bi.mass * clres)

    # -------------------------------------------

    return (np.allclose(cres, clres, rtol=1e-08, atol=1e-11),
            np.allclose(clres, cres, rtol=1e-08, atol=1e-11),
            cepot, clepot, np.sum(np.abs(cres - clres)))





def test_acc(cext, clext, bi, bj):
    # -------------------------------------------

    ni = len(bi)
    nj = len(bj)
    iposmass = np.vstack((bi.pos.T, bi.mass)).T
    jposmass = np.vstack((bj.pos.T, bj.mass)).T
    iveleps2 = np.vstack((bi.vel.T, bi.eps2)).T
    jveleps2 = np.vstack((bj.vel.T, bj.eps2)).T
    data = (iposmass, iveleps2,
            jposmass, jveleps2,
            np.uint32(ni),
            np.uint32(nj),
            np.float64(0.0))

    output_buf = np.empty((len(bi.acc),4))
    lmem_layout = (4, 4)

    # Adjusts global_size to be an integer multiple of local_size
    local_size = 384
    global_size = ((ni-1)//local_size + 1) * local_size

    # -------------------------------------------

    # XXX: kw has no efects with C extensions!
    cext.set_kernel_args(*data, global_size=global_size,
                                local_size=local_size,
                                output_buf=output_buf,
                                lmem_layout=lmem_layout)
    cext.run()
    cres = cext.get_result()
    c_com_force = (bi.mass * cres[:,:3].T).sum(1)
    c_com_force = np.dot(c_com_force, c_com_force)**0.5

    # -------------------------------------------

    clext.set_kernel_args(*data, global_size=global_size,
                                 local_size=local_size,
                                 output_buf=output_buf,
                                 lmem_layout=lmem_layout)
    clext.run()
    clres = clext.get_result()
    cl_com_force = (bi.mass * clres[:,:3].T).sum(1)
    cl_com_force = np.dot(cl_com_force, cl_com_force)**0.5

    # -------------------------------------------

    return (np.allclose(cres, clres, rtol=1e-08, atol=1e-11),
            np.allclose(clres, cres, rtol=1e-08, atol=1e-11),
            c_com_force, cl_com_force, np.sum(np.abs(cres - clres)))





def compare(test, cext, clext, bi):
    npart = len(bi)
    bj = bi.copy()

    if test.__name__ is "test_phi":
        epot = bi.get_total_epot()
    if test.__name__ is "test_acc":
        com_force = (bi.mass * bi.acc.T).sum(1)
        com_force = np.dot(com_force, com_force)**0.5


    print("\nRuning {0} (varying i with j fixed):".format(test.__name__))
    for i in range(1, npart+1):
        a, b, cret, clret, cdiffcl = test(cext, clext, bi[:i], bj)
        fmt = "{0:4d} {1:4d} {2:5s} {3:5s} {4:< .16e} {5:< .16e} {6:< .16e}"
        print(fmt.format(i, npart, a, b, cret, clret, cdiffcl))
        if not a or not b:
            print('Error!!! Exiting...')
            sys.exit(0)

    print(" "*22+"-"*47)
    if test.__name__ is "test_phi":
        print(" "*34+"Total epot: {0:< .16e}".format(epot))
    if test.__name__ is "test_acc":
        print(" "*30+"Total CoMforce: {0:< .16e}".format(com_force))

    print("\nRuning {0} (varying j with i fixed):".format(test.__name__))
    for i in range(1, npart+1):
        a, b, cret, clret, cdiffcl = test(cext, clext, bi, bj[:i])
        fmt = "{0:4d} {1:4d} {2:5s} {3:5s} {4:< .16e} {5:< .16e} {6:< .16e}"
        print(fmt.format(npart, i, a, b, cret, clret, cdiffcl))
        if not a or not b:
            print('Error!!! Exiting...')
            sys.exit(0)

    print(" "*22+"-"*47)
    if test.__name__ is "test_phi":
        print(" "*34+"Total epot: {0:< .16e}".format(epot))
    if test.__name__ is "test_acc":
        print(" "*30+"Total CoMforce: {0:< .16e}".format(com_force))

    print("\nRuning {0} (varying i and j)".format(test.__name__))
    for i in range(1, npart+1):
        a, b, cret, clret, cdiffcl = test(cext, clext, bi[:i], bj[:i])
        fmt = "{0:4d} {1:4d} {2:5s} {3:5s} {4:< .16e} {5:< .16e} {6:< .16e}"
        print(fmt.format(i, i, a, b, cret, clret, cdiffcl))
        if not a or not b:
            print('Error!!! Exiting...')
            sys.exit(0)

    print(" "*22+"-"*47)
    if test.__name__ is "test_phi":
        print(" "*34+"Total epot: {0:< .16e}".format(epot))
    if test.__name__ is "test_acc":
        print(" "*30+"Total CoMforce: {0:< .16e}".format(com_force))





def performance_test(cext, clext, ni, nj, data, output_shape, lmem_layout, nsamples=5):
    timer = Timer()

    output_buf = np.empty(eval(output_shape.format(ni=ni)))

    # Adjusts global_size to be an integer multiple of local_size
    local_size = 384
    global_size = ((ni-1)//local_size + 1) * local_size

    # -------------------------------------------

    print("\nRuning performance_test (average over {0} runs):".format(nsamples))

    # -------------------------------------------

    # XXX: kw has no efects with C extensions!
    cext.set_kernel_args(*data, global_size=global_size,
                                local_size=local_size,
                                output_buf=output_buf,
                                lmem_layout=lmem_layout)
    c_elapsed = 0.0
    for i in range(nsamples):
        timer.start()
        cext.run()
        c_elapsed += timer.elapsed()
    cres = cext.get_result()
    c_elapsed /= nsamples

    c_gflops = cext.flops_count * ni * nj * 1.0e-9
    c_metrics = {"time": c_elapsed,
                 "npart/s": np.sqrt(ni*nj)/c_elapsed,
                 "gflop/s": c_gflops/c_elapsed,
                 "kernel_name": cext.kernel_name}
    print("C metrics :", c_metrics)

    # -------------------------------------------

    clext.set_kernel_args(*data, global_size=global_size,
                                 local_size=local_size,
                                 output_buf=output_buf,
                                 lmem_layout=lmem_layout)
    cl_elapsed = 0.0
    for i in range(nsamples):
        timer.start()
        clext.run()
        cl_elapsed += timer.elapsed()
    clres = clext.get_result()
    cl_elapsed /= nsamples

    cl_gflops = clext.flops_count * ni * nj * 1.0e-9
    cl_metrics = {"time": cl_elapsed,
                  "npart/s": np.sqrt(ni*nj)/cl_elapsed,
                  "gflop/s": cl_gflops/cl_elapsed,
                  "kernel_name": clext.kernel_name}
    print("CL metrics:", cl_metrics)















def test_pnacc(cext, bi, bj):
    from pynbody.lib.gravity import Clight

    clight = Clight(4, 25.0)

    # -------------------------------------------

    ni = len(bi)
    nj = len(bj)
    iposmass = np.vstack((bi.pos.T, bi.mass)).T
    jposmass = np.vstack((bj.pos.T, bj.mass)).T
    data = (np.uint32(ni),
            np.uint32(nj),
            iposmass, bi.vel,
            jposmass, bj.vel,
            np.uint32(clight.pn_order), np.float64(clight.inv1),
            np.float64(clight.inv2), np.float64(clight.inv3),
            np.float64(clight.inv4), np.float64(clight.inv5),
            np.float64(clight.inv6), np.float64(clight.inv7)
           )

    # -------------------------------------------

    # XXX: kw has no efects with C extensions!
    cext.set_kernel_args(*data)
    cext.run()
    cres = cext.get_result()

    # -------------------------------------------

    return cres




if __name__ == "__main__":
#    run_all()
    unittest.main(verbosity=1)


########## end of file ##########
