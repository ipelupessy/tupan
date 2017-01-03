#include "acc_kernel_common.h"

/*
void
acc_kernel_impl(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[],
	global real_t __jadot[],
	local Acc_Data _jp[])
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
*/

/*
void
acc_kernel_impl(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[],
	global real_t __jadot[],
	local Acc_Data _jp[])
{
	uint_t lid = get_local_id(0);
	uint_t wid = get_group_id(0);
	uint_t wsize = get_num_groups(0);
	uint_t nsimd = (ni - SIMD) * (SIMD < ni);

	for (uint_t iii = SIMD * LSIZE * wid;
				iii < ni;
				iii += SIMD * LSIZE * wsize) {
		Acc_Data ip;
		uint_t ii = min(iii + SIMD * lid, nsimd);
		ip.m = vec(vload)(0, &__im[ii]);
		ip.e2 = vec(vload)(0, &__ie2[ii]);
		ip.rx = vec(vload)(0, &__irdot[(0*NDIM+0)*ni + ii]);
		ip.ry = vec(vload)(0, &__irdot[(0*NDIM+1)*ni + ii]);
		ip.rz = vec(vload)(0, &__irdot[(0*NDIM+2)*ni + ii]);
		ip.ax = (real_tn)(0);//vec(vload)(0, &__iadot[(0*NDIM+0)*ni + ii]);
		ip.ay = (real_tn)(0);//vec(vload)(0, &__iadot[(0*NDIM+1)*ni + ii]);
		ip.az = (real_tn)(0);//vec(vload)(0, &__iadot[(0*NDIM+2)*ni + ii]);
		uint_t j0 = 0;
		uint_t j1 = 0;
		#pragma unroll
		for (uint_t jlsize = LSIZE;
					jlsize > 0;
					jlsize >>= 1) {
			j0 = j1 + lid % jlsize;
			j1 = jlsize * (nj/jlsize);
			for (uint_t jj = j0;
						jj < j1;
						jj += jlsize) {
				Acc_Data jp;
				jp.m = (real_tn)(__jm[jj]);
				jp.e2 = (real_tn)(__je2[jj]);
				jp.rx = (real_tn)(__jrdot[(0*NDIM+0)*nj + jj]);
				jp.ry = (real_tn)(__jrdot[(0*NDIM+1)*nj + jj]);
				jp.rz = (real_tn)(__jrdot[(0*NDIM+2)*nj + jj]);
				jp.ax = (real_tn)(__jadot[(0*NDIM+0)*nj + jj]);
				jp.ay = (real_tn)(__jadot[(0*NDIM+1)*nj + jj]);
				jp.az = (real_tn)(__jadot[(0*NDIM+2)*nj + jj]);
				barrier(CLK_LOCAL_MEM_FENCE);
				_jp[lid] = jp;
				barrier(CLK_LOCAL_MEM_FENCE);
				#pragma unroll 8
				for (uint_t j = 0; j < jlsize; ++j) {
					ip = acc_kernel_core(ip, _jp[j]);
				}
			}
		}
		vec(vstore)(ip.ax, 0, &__iadot[(0*NDIM+0)*ni + ii]);
		vec(vstore)(ip.ay, 0, &__iadot[(0*NDIM+1)*ni + ii]);
		vec(vstore)(ip.az, 0, &__iadot[(0*NDIM+2)*ni + ii]);
	}
}
*/

/*
void
acc_kernel_impl(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[],
	global real_t __jadot[],
	local Acc_Data _jp[])
{
	uint_t lid = get_local_id(0);
	uint_t wid = get_group_id(0);
	uint_t wsize = get_num_groups(0);
	uint_t nsimd = (ni - SIMD) * (SIMD < ni);

	uint_t j0 = 0;
	uint_t j1 = 0;
	#pragma unroll
	for (uint_t jlsize = LSIZE;
				jlsize > 0;
				jlsize >>= 1) {
		j0 = j1 + lid % jlsize;
		j1 = jlsize * (nj/jlsize);
		for (uint_t jj = j0;
					jj < j1;
					jj += jlsize) {
			Acc_Data jp;
			jp.m = (real_tn)(__jm[jj]);
			jp.e2 = (real_tn)(__je2[jj]);
			jp.rx = (real_tn)(__jrdot[(0*NDIM+0)*nj + jj]);
			jp.ry = (real_tn)(__jrdot[(0*NDIM+1)*nj + jj]);
			jp.rz = (real_tn)(__jrdot[(0*NDIM+2)*nj + jj]);
			jp.ax = (real_tn)(__jadot[(0*NDIM+0)*nj + jj]);
			jp.ay = (real_tn)(__jadot[(0*NDIM+1)*nj + jj]);
			jp.az = (real_tn)(__jadot[(0*NDIM+2)*nj + jj]);
			barrier(CLK_LOCAL_MEM_FENCE);
			_jp[lid] = jp;
			for (uint_t iii = SIMD * LSIZE * wid;
						iii < ni;
						iii += SIMD * LSIZE * wsize) {
				Acc_Data ip;
				uint_t ii = min(iii + SIMD * lid, nsimd);
				ip.m = vec(vload)(0, &__im[ii]);
				ip.e2 = vec(vload)(0, &__ie2[ii]);
				ip.rx = vec(vload)(0, &__irdot[(0*NDIM+0)*ni + ii]);
				ip.ry = vec(vload)(0, &__irdot[(0*NDIM+1)*ni + ii]);
				ip.rz = vec(vload)(0, &__irdot[(0*NDIM+2)*ni + ii]);
				ip.ax = vec(vload)(0, &__iadot[(0*NDIM+0)*ni + ii]);
				ip.ay = vec(vload)(0, &__iadot[(0*NDIM+1)*ni + ii]);
				ip.az = vec(vload)(0, &__iadot[(0*NDIM+2)*ni + ii]);
				barrier(CLK_LOCAL_MEM_FENCE);
				#pragma unroll 8
				for (uint_t j = 0; j < jlsize; ++j) {
					ip = acc_kernel_core(ip, _jp[j]);
				}
				vec(vstore)(ip.ax, 0, &__iadot[(0*NDIM+0)*ni + ii]);
				vec(vstore)(ip.ay, 0, &__iadot[(0*NDIM+1)*ni + ii]);
				vec(vstore)(ip.az, 0, &__iadot[(0*NDIM+2)*ni + ii]);
			}
		}
	}
}
*/


void
acc_kernel_impl(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[],
	global real_t __jadot[],
	local Acc_Data _jp[])
{
	uint_t lid = get_local_id(0);
	uint_t wid = get_group_id(0);
	uint_t wsize = get_num_groups(0);

	for (uint_t iii = SIMD * LSIZE * wid;
				iii < ni;
				iii += SIMD * LSIZE * wsize) {
		Acc_Data ip;
		#pragma unroll
		for (uint_t i = 0; i < SIMD; ++i) {
			uint_t ii = (iii + i * LSIZE + lid) % ni;
			ip._m[i] = __im[ii];
			ip._e2[i] = __ie2[ii];
			ip._rx[i] = __irdot[(0*NDIM+0)*ni + ii];
			ip._ry[i] = __irdot[(0*NDIM+1)*ni + ii];
			ip._rz[i] = __irdot[(0*NDIM+2)*ni + ii];
			ip._ax[i] = 0;//__iadot[(0*NDIM+0)*ni + ii];
			ip._ay[i] = 0;//__iadot[(0*NDIM+1)*ni + ii];
			ip._az[i] = 0;//__iadot[(0*NDIM+2)*ni + ii];
		}
		uint_t j0 = 0;
		uint_t j1 = 0;
		#pragma unroll
		for (uint_t jlsize = LSIZE;
					jlsize > 0;
					jlsize >>= 1) {
			j0 = j1 + lid % jlsize;
			j1 = jlsize * (nj/jlsize);
			for (uint_t jj = j0;
						jj < j1;
						jj += jlsize) {
				Acc_Data jp;
				jp.m = (real_tn)(__jm[jj]);
				jp.e2 = (real_tn)(__je2[jj]);
				jp.rx = (real_tn)(__jrdot[(0*NDIM+0)*nj + jj]);
				jp.ry = (real_tn)(__jrdot[(0*NDIM+1)*nj + jj]);
				jp.rz = (real_tn)(__jrdot[(0*NDIM+2)*nj + jj]);
				jp.ax = (real_tn)(__jadot[(0*NDIM+0)*nj + jj]);
				jp.ay = (real_tn)(__jadot[(0*NDIM+1)*nj + jj]);
				jp.az = (real_tn)(__jadot[(0*NDIM+2)*nj + jj]);
				barrier(CLK_LOCAL_MEM_FENCE);
				_jp[lid] = jp;
				barrier(CLK_LOCAL_MEM_FENCE);
				#pragma unroll 8
				for (uint_t j = 0; j < jlsize; ++j) {
					ip = acc_kernel_core(ip, _jp[j]);
				}
			}
		}
		#pragma unroll
		for (uint_t i = 0; i < SIMD; ++i) {
			uint_t ii = (iii + i * LSIZE + lid) % ni;
			__iadot[(0*NDIM+0)*ni + ii] = ip._ax[i];
			__iadot[(0*NDIM+1)*ni + ii] = ip._ay[i];
			__iadot[(0*NDIM+2)*ni + ii] = ip._az[i];
		}
	}
}


kernel void
acc_kernel_rectangle(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	const uint_t nj,
	global const real_t __jm[],
	global const real_t __je2[],
	global const real_t __jrdot[],
	global real_t __iadot[],
	global real_t __jadot[])
{
	local Acc_Data _pAcc[LSIZE];

	acc_kernel_impl(
		ni, __im, __ie2, __irdot,
		nj, __jm, __je2, __jrdot,
		__iadot, __jadot,
		_pAcc
	);

	barrier(CLK_GLOBAL_MEM_FENCE);

	acc_kernel_impl(
		nj, __jm, __je2, __jrdot,
		ni, __im, __ie2, __irdot,
		__jadot, __iadot,
		_pAcc
	);
}


kernel void
acc_kernel_triangle(
	const uint_t ni,
	global const real_t __im[],
	global const real_t __ie2[],
	global const real_t __irdot[],
	global real_t __iadot[])
{
	local Acc_Data _pAcc[LSIZE];

	acc_kernel_impl(
		ni, __im, __ie2, __irdot,
		ni, __im, __ie2, __irdot,
		__iadot, __iadot,
		_pAcc
	);
}

