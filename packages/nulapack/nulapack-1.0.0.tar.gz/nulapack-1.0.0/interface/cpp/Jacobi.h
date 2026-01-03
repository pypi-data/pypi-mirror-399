#ifndef JACOBI_H
#define JACOBI_H

#include "types.h"
#include "mangling.h"

/* =========================
 * FORTRAN API DECLARATIONS
 * ========================= */

fortran API_cgejsv(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                   INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_dgejsv(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                   INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);

fortran API_sgejsv(INTEGER* N, REAL* A, REAL* B, REAL* X,
                   INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_zgejsv(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                   INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);


#ifdef __cplusplus

    /* ==============
     * C++ INTERFACE
     * ============== */

    SUBROUTINE JACOBI(INTEGER* N, REAL* A, REAL* B, REAL* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_sgejsv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE JACOBI(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_dgejsv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE JACOBI(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_cgejsv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE JACOBI(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_zgejsv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

#else  // C-only fallback

    /* ===========
     * C INTERFACE
     * ============ */

    #define JACOBI(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)  \
        _Generic((A),                                                \
            REAL*:            API_sgejsv,                            \
            DOUBLE*:          API_dgejsv,                            \
            COMPLEX*:         API_cgejsv,                            \
            DOUBLE_COMPLEX*:  API_zgejsv                             \
        )(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)

#endif

#endif
