#ifndef FORTRAN_TYPES_H
#define FORTRAN_TYPES_H

#include <stdint.h>
#include <inttypes.h>

#ifdef __cplusplus
  #include <complex>
  typedef std::complex<float>  complex_float;
  typedef std::complex<double> complex_double;
#else
  #include <complex.h>
  typedef float _Complex  complex_float;
  typedef double _Complex complex_double;
#endif

/* Accessors for real/imaginary parts */
#ifndef complex_float_real
  #define complex_float_real(z)   (crealf(z))
#endif
#ifndef complex_float_imag
  #define complex_float_imag(z)   (cimagf(z))
#endif
#ifndef complex_double_real
  #define complex_double_real(z)  (creal(z))
#endif
#ifndef complex_double_imag
  #define complex_double_imag(z)  (cimag(z))
#endif

/* Integer type — default is 32-bit, override with -DFORTRAN_ILP64 if needed */
#ifdef FORTRAN_ILP64
  typedef int64_t fortran_int;
  #define FORTRAN_IFMT PRId64
#else
  typedef int32_t fortran_int;
  #define FORTRAN_IFMT PRId32
#endif

typedef fortran_int fortran_logical;

/* Fortran-style type aliases */
typedef float           fortran_real;
typedef double          fortran_double;
typedef complex_float   fortran_complex;
typedef complex_double  fortran_double_complex;

/* Aliases matching traditional Fortran naming */
#define REAL            fortran_real
#define DOUBLE          fortran_double
#define COMPLEX         fortran_complex
#define DOUBLE_COMPLEX  fortran_double_complex
#define INTEGER         fortran_int
#define LOGICAL         fortran_logical

/* Optional: function pointer types for selector functions */
typedef LOGICAL (*SELECT_REAL_2)(const REAL*, const REAL*);
typedef LOGICAL (*SELECT_REAL_3)(const REAL*, const REAL*, const REAL*);
typedef LOGICAL (*SELECT_DOUBLE_2)(const DOUBLE*, const DOUBLE*);
typedef LOGICAL (*SELECT_DOUBLE_3)(const DOUBLE*, const DOUBLE*, const DOUBLE*);
typedef LOGICAL (*SELECT_COMPLEX_1)(const COMPLEX*);
typedef LOGICAL (*SELECT_COMPLEX_2)(const COMPLEX*, const COMPLEX*);
typedef LOGICAL (*SELECT_DOUBLE_COMPLEX_1)(const DOUBLE_COMPLEX*);
typedef LOGICAL (*SELECT_DOUBLE_COMPLEX_2)(const DOUBLE_COMPLEX*, const DOUBLE_COMPLEX*);

#define SUBROUTINE inline void

#ifdef __cplusplus
    #define fortran extern "C" void
#else
    #define fortran extern void
#endif

#endif
