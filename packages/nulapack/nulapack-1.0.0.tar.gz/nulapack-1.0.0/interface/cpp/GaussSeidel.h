#ifndef GAUSS_SEIDEL_H
#define GAUSS_SEIDEL_H

#include "types.h"
#include "mangling.h"

/* =========================
 * FORTRAN API DECLARATIONS
 * ========================= */

fortran API_cgegssv(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                   INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_dgegssv(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                   INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);

fortran API_sgegssv(INTEGER* N, REAL* A, REAL* B, REAL* X,
                   INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_zgegssv(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                   INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);


#ifdef __cplusplus

    /* ==============
     * C++ INTERFACE
     * ============== */

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, REAL* A, REAL* B, REAL* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_sgegssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_dgegssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_cgegssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_zgegssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

#else  // C-only fallback

    /* ===========
     * C INTERFACE
     * ============ */

    #define GAUSS_SEIDEL(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)  \
        _Generic((A),                                                \
            REAL*:            API_sgegssv,                            \
            DOUBLE*:          API_dgegssv,                            \
            COMPLEX*:         API_cgegssv,                            \
            DOUBLE_COMPLEX*:  API_zgegssv                             \
        )(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)

#endif

#endif
