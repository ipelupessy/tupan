#include "tstep_kernel_common.h"


inline REAL
accum_tstep(
    REAL iomega,
    const REAL8 idata,
    const REAL eta,
    uint j_begin,
    uint j_end,
    __local REAL *shr_jrx,
    __local REAL *shr_jry,
    __local REAL *shr_jrz,
    __local REAL *shr_jmass,
    __local REAL *shr_jvx,
    __local REAL *shr_jvy,
    __local REAL *shr_jvz,
    __local REAL *shr_jeps2
    )
{
    uint j;
    for (j = j_begin; j < j_end; ++j) {
        REAL8 jdata = (REAL8){shr_jrx[j], shr_jry[j], shr_jrz[j], shr_jmass[j],
                              shr_jvx[j], shr_jvy[j], shr_jvz[j], shr_jeps2[j]};
        iomega = tstep_kernel_core(iomega,
                                   idata.lo, idata.hi,
                                   jdata.lo, jdata.hi,
                                   eta);
    }
    return iomega;
}


inline REAL
tstep_kernel_main_loop(
    const REAL8 idata,
    const uint nj,
    __global const REAL *inp_jrx,
    __global const REAL *inp_jry,
    __global const REAL *inp_jrz,
    __global const REAL *inp_jmass,
    __global const REAL *inp_jvx,
    __global const REAL *inp_jvy,
    __global const REAL *inp_jvz,
    __global const REAL *inp_jeps2,
    const REAL eta,
    __local REAL *shr_jrx,
    __local REAL *shr_jry,
    __local REAL *shr_jrz,
    __local REAL *shr_jmass,
    __local REAL *shr_jvx,
    __local REAL *shr_jvy,
    __local REAL *shr_jvz,
    __local REAL *shr_jeps2
    )
{
    uint lsize = get_local_size(0);

    REAL iomega = (REAL)0;

    uint tile;
    uint numTiles = (nj - 1)/lsize + 1;
    for (tile = 0; tile < numTiles; ++tile) {
        uint nb = min(lsize, (nj - (tile * lsize)));

        event_t e[8];
        e[0] = async_work_group_copy(shr_jrx, inp_jrx + tile * lsize, nb, 0);
        e[1] = async_work_group_copy(shr_jry, inp_jry + tile * lsize, nb, 0);
        e[2] = async_work_group_copy(shr_jrz, inp_jrz + tile * lsize, nb, 0);
        e[3] = async_work_group_copy(shr_jmass, inp_jmass + tile * lsize, nb, 0);
        e[4] = async_work_group_copy(shr_jvx, inp_jvx + tile * lsize, nb, 0);
        e[5] = async_work_group_copy(shr_jvy, inp_jvy + tile * lsize, nb, 0);
        e[6] = async_work_group_copy(shr_jvz, inp_jvz + tile * lsize, nb, 0);
        e[7] = async_work_group_copy(shr_jeps2, inp_jeps2 + tile * lsize, nb, 0);
        wait_group_events(8, e);

        uint j = 0;
        uint j_max = (nb > (JUNROLL - 1)) ? (nb - (JUNROLL - 1)):(0);
        for (; j < j_max; j += JUNROLL) {
            iomega = accum_tstep(iomega, idata,
                                 eta, j, j + JUNROLL,
                                 shr_jrx, shr_jry, shr_jrz, shr_jmass,
                                 shr_jvx, shr_jvy, shr_jvz, shr_jeps2);
        }
        iomega = accum_tstep(iomega, idata,
                             eta, j, nb,
                             shr_jrx, shr_jry, shr_jrz, shr_jmass,
                             shr_jvx, shr_jvy, shr_jvz, shr_jeps2);

        barrier(CLK_LOCAL_MEM_FENCE);
    }

    return iomega;
}


__kernel void
tstep_kernel(
    const uint ni,
    __global const REAL *inp_irx,
    __global const REAL *inp_iry,
    __global const REAL *inp_irz,
    __global const REAL *inp_imass,
    __global const REAL *inp_ivx,
    __global const REAL *inp_ivy,
    __global const REAL *inp_ivz,
    __global const REAL *inp_ieps2,
    const uint nj,
    __global const REAL *inp_jrx,
    __global const REAL *inp_jry,
    __global const REAL *inp_jrz,
    __global const REAL *inp_jmass,
    __global const REAL *inp_jvx,
    __global const REAL *inp_jvy,
    __global const REAL *inp_jvz,
    __global const REAL *inp_jeps2,
    const REAL eta,
    __global REAL *out_idt,
    __local REAL *shr_jrx,
    __local REAL *shr_jry,
    __local REAL *shr_jrz,
    __local REAL *shr_jmass,
    __local REAL *shr_jvx,
    __local REAL *shr_jvy,
    __local REAL *shr_jvz,
    __local REAL *shr_jeps2
    )
{
    uint gid = get_global_id(0);
    uint i = (gid < ni) ? (gid) : (ni-1);

    REAL8 idata = (REAL8){inp_irx[i], inp_iry[i], inp_irz[i], inp_imass[i],
                          inp_ivx[i], inp_ivy[i], inp_ivz[i], inp_ieps2[i]};

    REAL iomega = tstep_kernel_main_loop(idata,
                                         nj,
                                         inp_jrx, inp_jry, inp_jrz, inp_jmass,
                                         inp_jvx, inp_jvy, inp_jvz, inp_jeps2,
                                         eta,
                                         shr_jrx, shr_jry, shr_jrz, shr_jmass,
                                         shr_jvx, shr_jvy, shr_jvz, shr_jeps2);

//    out_idt[i] = 2 * eta / iomega;
    out_idt[i] = 2 * eta / sqrt(iomega);
}

