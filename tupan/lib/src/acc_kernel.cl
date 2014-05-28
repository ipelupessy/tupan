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
    UINT lid = get_local_id(0);
    UINT lsize = get_local_size(0);
    UINT i = VW * lsize * get_group_id(0);

    UINT mask = (i + VW * lid) < ni;
    mask *= lid;

    REALn im = vloadn(mask, _im + i);
    REALn irx = vloadn(mask, _irx + i);
    REALn iry = vloadn(mask, _iry + i);
    REALn irz = vloadn(mask, _irz + i);
    REALn ie2 = vloadn(mask, _ie2 + i);

    REALn iax = (REALn)(0);
    REALn iay = (REALn)(0);
    REALn iaz = (REALn)(0);

    UINT j = 0;

    #ifdef FAST_LOCAL_MEM
        __local REAL __jm[LSIZE];
        __local REAL __jrx[LSIZE];
        __local REAL __jry[LSIZE];
        __local REAL __jrz[LSIZE];
        __local REAL __je2[LSIZE];
        for (; (j + lsize - 1) < nj; j += lsize) {
            __jm[lid] = _jm[j + lid];
            __jrx[lid] = _jrx[j + lid];
            __jry[lid] = _jry[j + lid];
            __jrz[lid] = _jrz[j + lid];
            __je2[lid] = _je2[j + lid];
            barrier(CLK_LOCAL_MEM_FENCE);
            #pragma unroll UNROLL
            for (UINT k = 0; k < lsize; ++k) {
                acc_kernel_core(
                    im, irx, iry, irz, ie2,
                    __jm[k], __jrx[k], __jry[k], __jrz[k], __je2[k],
                    &iax, &iay, &iaz);
            }
            barrier(CLK_LOCAL_MEM_FENCE);
        }
    #endif

    #pragma unroll UNROLL
    for (; j < nj; ++j) {
        acc_kernel_core(
            im, irx, iry, irz, ie2,
            _jm[j], _jrx[j], _jry[j], _jrz[j], _je2[j],
            &iax, &iay, &iaz);
    }

    vstoren(iax, mask, _iax + i);
    vstoren(iay, mask, _iay + i);
    vstoren(iaz, mask, _iaz + i);
}

