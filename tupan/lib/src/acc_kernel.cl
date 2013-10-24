#include "acc_kernel_common.h"


__kernel void acc_kernel(
    const UINT ni,
    __global const REAL * restrict _im,
    __global const REAL * restrict _irx,
    __global const REAL * restrict _iry,
    __global const REAL * restrict _irz,
    __global const REAL * restrict _ie2,
    const UINT nj,
    __global const REAL * restrict _jm,
    __global const REAL * restrict _jrx,
    __global const REAL * restrict _jry,
    __global const REAL * restrict _jrz,
    __global const REAL * restrict _je2,
    __global REAL * restrict _iax,
    __global REAL * restrict _iay,
    __global REAL * restrict _iaz)
{
    UINT lsize = (get_local_size(0) + UNROLL - 1) / UNROLL;
    lsize = min(lsize, (UINT)(LSIZE));
    UINT lid = get_local_id(0) % lsize;
    UINT gid = get_global_id(0);

    REALn im = vloadn(gid, _im);
    REALn irx = vloadn(gid, _irx);
    REALn iry = vloadn(gid, _iry);
    REALn irz = vloadn(gid, _irz);
    REALn ie2 = vloadn(gid, _ie2);
    REALn iax = (REALn)(0);
    REALn iay = (REALn)(0);
    REALn iaz = (REALn)(0);

    UINT j = 0;
    __local concat(REAL, UNROLL) __jm[LSIZE];
    __local concat(REAL, UNROLL) __jrx[LSIZE];
    __local concat(REAL, UNROLL) __jry[LSIZE];
    __local concat(REAL, UNROLL) __jrz[LSIZE];
    __local concat(REAL, UNROLL) __je2[LSIZE];
    for (; (j + UNROLL * lsize) < nj; j += UNROLL * lsize) {
        concat(REAL, UNROLL) jm = concat(vload, UNROLL)(lid, _jm + j);
        concat(REAL, UNROLL) jrx = concat(vload, UNROLL)(lid, _jrx + j);
        concat(REAL, UNROLL) jry = concat(vload, UNROLL)(lid, _jry + j);
        concat(REAL, UNROLL) jrz = concat(vload, UNROLL)(lid, _jrz + j);
        concat(REAL, UNROLL) je2 = concat(vload, UNROLL)(lid, _je2 + j);
        barrier(CLK_LOCAL_MEM_FENCE);
        __jm[lid] = jm;
        __jrx[lid] = jrx;
        __jry[lid] = jry;
        __jrz[lid] = jrz;
        __je2[lid] = je2;
        barrier(CLK_LOCAL_MEM_FENCE);
        for (UINT k = 0; k < lsize; ++k) {
            jm = __jm[k];
            jrx = __jrx[k];
            jry = __jry[k];
            jrz = __jrz[k];
            je2 = __je2[k];
            #if UNROLL == 1
                acc_kernel_core(im, irx, iry, irz, ie2,
                                jm, jrx, jry, jrz, je2,
                                &iax, &iay, &iaz);
            #else
                #pragma unroll
                for (UINT l = 0; l < UNROLL; ++l) {
                    acc_kernel_core(im, irx, iry, irz, ie2,
                                    jm.s0, jrx.s0, jry.s0, jrz.s0, je2.s0,
                                    &iax, &iay, &iaz);
                    jm = shuffle(jm, MASK);
                    jrx = shuffle(jrx, MASK);
                    jry = shuffle(jry, MASK);
                    jrz = shuffle(jrz, MASK);
                    je2 = shuffle(je2, MASK);
                }
            #endif
        }
    }
    for (; j < nj; ++j) {
        acc_kernel_core(im, irx, iry, irz, ie2,
                        _jm[j], _jrx[j], _jry[j], _jrz[j], _je2[j],
                        &iax, &iay, &iaz);
    }

    vstoren(iax, gid, _iax);
    vstoren(iay, gid, _iay);
    vstoren(iaz, gid, _iaz);
}

