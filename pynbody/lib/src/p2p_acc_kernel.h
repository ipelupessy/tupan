#ifndef P2P_ACC_KERNEL_H
#define P2P_ACC_KERNEL_H

#include"common.h"
#include"smoothing.h"

//
// p2p_acc_kernel_core
////////////////////////////////////////////////////////////////////////////////
inline REAL3
p2p_acc_kernel_core(REAL3 acc,
                    const REAL4 ri, const REAL hi2,
                    const REAL4 rj, const REAL hj2)
{
    REAL4 r;
    r.x = ri.x - rj.x;                                               // 1 FLOPs
    r.y = ri.y - rj.y;                                               // 1 FLOPs
    r.z = ri.z - rj.z;                                               // 1 FLOPs
    REAL r2 = r.x * r.x + r.y * r.y + r.z * r.z;                     // 5 FLOPs
    REAL inv_r3 = acc_smooth(r2, hi2 + hj2);                         // 5 FLOPs

    inv_r3 *= rj.w;                                                  // 1 FLOPs

    acc.x -= inv_r3 * r.x;                                           // 2 FLOPs
    acc.y -= inv_r3 * r.y;                                           // 2 FLOPs
    acc.z -= inv_r3 * r.z;                                           // 2 FLOPs
    return acc;
}
// Total flop count: 20


#ifdef __OPENCL_VERSION__
//
// OpenCL implementation
////////////////////////////////////////////////////////////////////////////////
inline REAL3
p2p_accum_acc(REAL3 myAcc,
              const REAL8 myData,
              uint j_begin,
              uint j_end,
              __local REAL8 *sharedJData
             )
{
    uint j;
    for (j = j_begin; j < j_end; ++j) {
        myAcc = p2p_acc_kernel_core(myAcc, myData.lo, myData.s7,
                                    sharedJData[j].lo, sharedJData[j].s7);
    }
    return myAcc;
}


inline REAL4
p2p_acc_kernel_main_loop(const REAL8 myData,
                         const uint nj,
                         __global const REAL8 *jdata,
                         __local REAL8 *sharedJData
                        )
{
    uint lsize = get_local_size(0);

    REAL3 myAcc = (REAL3){0, 0, 0};

    uint tile;
    uint numTiles = (nj - 1)/lsize + 1;
    for (tile = 0; tile < numTiles; ++tile) {
        uint nb = min(lsize, (nj - (tile * lsize)));

        event_t e[1];
        e[0] = async_work_group_copy(sharedJData, jdata + tile * lsize, nb, 0);
        wait_group_events(1, e);

        uint j = 0;
        uint j_max = (nb > (JUNROLL - 1)) ? (nb - (JUNROLL - 1)):(0);
        for (; j < j_max; j += JUNROLL) {
            myAcc = p2p_accum_acc(myAcc, myData,
                                  j, j + JUNROLL,
                                  sharedJData);
        }
        myAcc = p2p_accum_acc(myAcc, myData,
                              j, nb,
                              sharedJData);

        barrier(CLK_LOCAL_MEM_FENCE);
    }

    return (REAL4){myAcc.x, myAcc.y, myAcc.z, 0};
}


__kernel void p2p_acc_kernel(const uint ni,
                             __global const REAL8 *idata,
                             const uint nj,
                             __global const REAL8 *jdata,
                             __global REAL4 *iacc,  // XXX: Bug!!! if we use __global REAL3
                             __local REAL8 *sharedJData
                            )
{
    uint gid = get_global_id(0);
    uint i = (gid < ni) ? (gid) : (ni-1);
    iacc[i] = p2p_acc_kernel_main_loop(idata[i],
                                       nj, jdata,
                                       sharedJData);
}

#else
//
// C implementation
////////////////////////////////////////////////////////////////////////////////
static PyObject *
_p2p_acc_kernel(PyObject *_args)
{
    unsigned int ni, nj;
    PyObject *_idata = NULL;
    PyObject *_jdata = NULL;

    int typenum;
    char *fmt = NULL;
    if (sizeof(REAL) == sizeof(double)) {
        fmt = "IOIO";
        typenum = NPY_FLOAT64;
    } else if (sizeof(REAL) == sizeof(float)) {
        fmt = "IOIO";
        typenum = NPY_FLOAT32;
    }

    if (!PyArg_ParseTuple(_args, fmt, &ni, &_idata,
                                      &nj, &_jdata))
        return NULL;

    // i-data
    PyObject *_idata_arr = PyArray_FROM_OTF(_idata, typenum, NPY_IN_ARRAY);
    REAL *idata_ptr = (REAL *)PyArray_DATA(_idata_arr);

    // j-data
    PyObject *_jdata_arr = PyArray_FROM_OTF(_jdata, typenum, NPY_IN_ARRAY);
    REAL *jdata_ptr = (REAL *)PyArray_DATA(_jdata_arr);

    // allocate a PyArrayObject to be returned
    npy_intp dims[2] = {ni, 3};
    PyArrayObject *ret = (PyArrayObject *)PyArray_EMPTY(2, dims, typenum, 0);
    REAL *ret_ptr = (REAL *)PyArray_DATA(ret);

    // main calculation
    unsigned int i, i3, i8, j, j8;
    for (i = 0; i < ni; ++i) {
        i8 = 8*i;
        REAL3 iacc = (REAL3){0, 0, 0};
        REAL4 ri = {idata_ptr[i8  ], idata_ptr[i8+1],
                    idata_ptr[i8+2], idata_ptr[i8+3]};
        REAL ieps2 = idata_ptr[i8+7];
        for (j = 0; j < nj; ++j) {
            j8 = 8*j;
            REAL4 rj = {jdata_ptr[j8  ], jdata_ptr[j8+1],
                        jdata_ptr[j8+2], jdata_ptr[j8+3]};
            REAL jeps2 = jdata_ptr[j8+7];
            iacc = p2p_acc_kernel_core(iacc, ri, ieps2, rj, jeps2);
        }
        i3 = 3*i;
        ret_ptr[i3  ] = iacc.x;
        ret_ptr[i3+1] = iacc.y;
        ret_ptr[i3+2] = iacc.z;
    }

    // Decrement the reference counts for i-objects
    Py_DECREF(_idata_arr);

    // Decrement the reference counts for j-objects
    Py_DECREF(_jdata_arr);

    // returns a PyArrayObject
    return PyArray_Return(ret);
}

#endif  // __OPENCL_VERSION__


#endif  // P2P_ACC_KERNEL_H

