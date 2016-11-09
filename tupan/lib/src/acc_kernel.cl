#include "acc_kernel_common.h"


kernel void
acc_kernel(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[])
{
	for (uint_t ii = SIMD * get_group_id(0) * get_local_size(0);
				ii < ni;
				ii += SIMD * get_num_groups(0) * get_local_size(0)) {
		uint_t lid = get_local_id(0);
		uint_t i = ii + SIMD * lid;
		i = min(i, ni-SIMD);
		i *= (SIMD < ni);

		Acc_Data ip;
		ip.m = vec(vload)(0, __im + i);
		ip.e2 = vec(vload)(0, __ie2 + i);
		ip.rx = vec(vload)(0, &__irdot[(0*NDIM+0)*ni + i]);
		ip.ry = vec(vload)(0, &__irdot[(0*NDIM+1)*ni + i]);
		ip.rz = vec(vload)(0, &__irdot[(0*NDIM+2)*ni + i]);
		ip.ax = (real_tn)(0);
		ip.ay = (real_tn)(0);
		ip.az = (real_tn)(0);

		uint_t j = 0;

		#ifdef FAST_LOCAL_MEM
		for (; (j + LSIZE - 1) < nj; j += LSIZE) {
			Acc_Data jp;
			jp.m = (real_tn)(__jm[j + lid]);
			jp.e2 = (real_tn)(__je2[j + lid]);
			jp.rx = (real_tn)(__jrdot[(0*NDIM+0)*nj + j + lid]);
			jp.ry = (real_tn)(__jrdot[(0*NDIM+1)*nj + j + lid]);
			jp.rz = (real_tn)(__jrdot[(0*NDIM+2)*nj + j + lid]);
			jp.ax = (real_tn)(0);
			jp.ay = (real_tn)(0);
			jp.az = (real_tn)(0);
			barrier(CLK_LOCAL_MEM_FENCE);
			local Acc_Data _jp[LSIZE];
			_jp[lid] = jp;
			barrier(CLK_LOCAL_MEM_FENCE);
			#pragma unroll 8
			for (uint_t k = 0; k < LSIZE; ++k) {
				jp = _jp[k];
				ip = acc_kernel_core(ip, jp);
			}
		}
		#endif

		for (; j < nj; ++j) {
			Acc_Data jp;
			jp.m = (real_tn)(__jm[j]);
			jp.e2 = (real_tn)(__je2[j]);
			jp.rx = (real_tn)(__jrdot[(0*NDIM+0)*nj + j]);
			jp.ry = (real_tn)(__jrdot[(0*NDIM+1)*nj + j]);
			jp.rz = (real_tn)(__jrdot[(0*NDIM+2)*nj + j]);
			jp.ax = (real_tn)(0);
			jp.ay = (real_tn)(0);
			jp.az = (real_tn)(0);
			ip = acc_kernel_core(ip, jp);
		}

		vec(vstore)(ip.ax, 0, &__iadot[(0*NDIM+0)*ni + i]);
		vec(vstore)(ip.ay, 0, &__iadot[(0*NDIM+1)*ni + i]);
		vec(vstore)(ip.az, 0, &__iadot[(0*NDIM+2)*ni + i]);
	}
}

