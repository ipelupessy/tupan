#ifndef __ACC_KERNEL_COMMON_H__
#define __ACC_KERNEL_COMMON_H__


#include "common.h"


#ifdef __cplusplus	// cpp only, i.e., not for OpenCL
namespace Acc {

template<size_t TILE>
struct Acc_Data_SoA {
	real_t __ALIGNED__ m[TILE];
	real_t __ALIGNED__ e2[TILE];
	real_t __ALIGNED__ rx[TILE];
	real_t __ALIGNED__ ry[TILE];
	real_t __ALIGNED__ rz[TILE];
	real_t __ALIGNED__ ax[TILE];
	real_t __ALIGNED__ ay[TILE];
	real_t __ALIGNED__ az[TILE];
};

template<size_t TILE>
auto setup(
	const uint_t n,
	const real_t __m[],
	const real_t __e2[],
	const real_t __rdot[])
{
	auto ntiles = (n + TILE - 1) / TILE;
	vector<Acc_Data_SoA<TILE>> part(ntiles);
	for (size_t k = 0; k < n; ++k) {
		auto kk = k%TILE;
		auto& p = part[k/TILE];
		p.m[kk] = __m[k];
		p.e2[kk] = __e2[k];
		p.rx[kk] = __rdot[(0*NDIM+0)*n + k];
		p.ry[kk] = __rdot[(0*NDIM+1)*n + k];
		p.rz[kk] = __rdot[(0*NDIM+2)*n + k];
	}
	return part;
}

template<size_t TILE, typename PART>
void commit(const uint_t n, const PART& part, real_t __adot[])
{
	for (size_t k = 0; k < n; ++k) {
		auto kk = k%TILE;
		auto& p = part[k/TILE];
		__adot[(0*NDIM+0)*n + k] = p.ax[kk];
		__adot[(0*NDIM+1)*n + k] = p.ay[kk];
		__adot[(0*NDIM+2)*n + k] = p.az[kk];
	}
}

template<size_t TILE>
struct P2P_acc_kernel_core {
	template<typename IP, typename JP>
	void operator()(IP&& ip, JP&& jp) {
		// flop count: 28
		for (size_t i = 0; i < TILE; ++i) {
			auto iax = ip.ax[i];
			auto iay = ip.ay[i];
			auto iaz = ip.az[i];
			#pragma omp simd
			for (size_t j = 0; j < TILE; ++j) {
				auto ee = ip.e2[i] + jp.e2[j];
				auto rx = ip.rx[i] - jp.rx[j];
				auto ry = ip.ry[i] - jp.ry[j];
				auto rz = ip.rz[i] - jp.rz[j];

				auto rr = ee;
				rr += rx * rx + ry * ry + rz * rz;

				auto inv_r3 = rsqrt(rr);
				inv_r3 *= inv_r3 * inv_r3;

				auto im_r3 = ip.m[i] * inv_r3;
				jp.ax[j] += im_r3 * rx;
				jp.ay[j] += im_r3 * ry;
				jp.az[j] += im_r3 * rz;

				auto jm_r3 = jp.m[j] * inv_r3;
				iax -= jm_r3 * rx;
				iay -= jm_r3 * ry;
				iaz -= jm_r3 * rz;
			}
			ip.ax[i] = iax;
			ip.ay[i] = iay;
			ip.az[i] = iaz;
		}
	}

	template<typename P>
	void operator()(P&& p) {
		// flop count: 21
		for (size_t i = 0; i < TILE; ++i) {
			#pragma omp simd
			for (size_t j = 0; j < TILE; ++j) {
				auto ee = p.e2[i] + p.e2[j];
				auto rx = p.rx[i] - p.rx[j];
				auto ry = p.ry[i] - p.ry[j];
				auto rz = p.rz[i] - p.rz[j];

				auto rr = ee;
				rr += rx * rx + ry * ry + rz * rz;

				auto inv_r3 = rsqrt(rr);
				inv_r3 = (rr > ee) ? (inv_r3):(0);
				inv_r3 *= inv_r3 * inv_r3;

				auto im_r3 = p.m[i] * inv_r3;

				p.ax[j] += im_r3 * rx;
				p.ay[j] += im_r3 * ry;
				p.az[j] += im_r3 * rz;
			}
		}
	}
};

}	// namespace Acc
#else


// ----------------------------------------------------------------------------


typedef struct acc_data {
	union {
		real_tn m[WPT];
		real_t _m[WPT * SIMD];
	};
	union {
		real_tn e2[WPT];
		real_t _e2[WPT * SIMD];
	};
	union {
		real_tn rx[WPT];
		real_t _rx[WPT * SIMD];
	};
	union {
		real_tn ry[WPT];
		real_t _ry[WPT * SIMD];
	};
	union {
		real_tn rz[WPT];
		real_t _rz[WPT * SIMD];
	};
	union {
		real_tn ax[WPT];
		real_t _ax[WPT * SIMD];
	};
	union {
		real_tn ay[WPT];
		real_t _ay[WPT * SIMD];
	};
	union {
		real_tn az[WPT];
		real_t _az[WPT * SIMD];
	};
} Acc_Data;


typedef struct acc_data_soa {
	union {
		real_tn m[NLANES];
		real_t _m[NLANES * SIMD];
	};
	union {
		real_tn e2[NLANES];
		real_t _e2[NLANES * SIMD];
	};
	union {
		real_tn rx[NLANES];
		real_t _rx[NLANES * SIMD];
	};
	union {
		real_tn ry[NLANES];
		real_t _ry[NLANES * SIMD];
	};
	union {
		real_tn rz[NLANES];
		real_t _rz[NLANES * SIMD];
	};
	union {
		real_tn ax[NLANES];
		real_t _ax[NLANES * SIMD];
	};
	union {
		real_tn ay[NLANES];
		real_t _ay[NLANES * SIMD];
	};
	union {
		real_tn az[NLANES];
		real_t _az[NLANES * SIMD];
	};
} Acc_Data_SoA;


static inline void
read_Acc_Data(
	const uint_t nloads,
	const uint_t base,
	const uint_t lid,
	Acc_Data *p,
	const uint_t n,
	global const real_t __m[],
	global const real_t __e2[],
	global const real_t __rdot[])
{
	for (uint_t k = 0, kk = base + lid;
				k < nloads;
				k += 1, kk += WGSIZE) {
		if (kk < n) {
			p->_m[k] = __m[kk];
			p->_e2[k] = __e2[kk];
			p->_rx[k] = (__rdot+(0*NDIM+0)*n)[kk];
			p->_ry[k] = (__rdot+(0*NDIM+1)*n)[kk];
			p->_rz[k] = (__rdot+(0*NDIM+2)*n)[kk];
		}
	}
}


static inline void
simd_shuff_Acc_Data(
	const uint_t k,
	Acc_Data *p)
{
	shuff(p->m[k], SIMD);
	shuff(p->e2[k], SIMD);
	shuff(p->rx[k], SIMD);
	shuff(p->ry[k], SIMD);
	shuff(p->rz[k], SIMD);
	shuff(p->ax[k], SIMD);
	shuff(p->ay[k], SIMD);
	shuff(p->az[k], SIMD);
}


#endif	// __cplusplus
#endif	// __ACC_KERNEL_COMMON_H__
