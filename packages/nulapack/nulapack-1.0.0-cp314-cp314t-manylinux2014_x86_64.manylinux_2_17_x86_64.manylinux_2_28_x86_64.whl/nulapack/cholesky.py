import _nulapack
import numpy as np


def cholesky(a: np.ndarray):
    """
    Compute the Cholesky factorization of a symmetric/Hermitian
    positive-definite matrix A using NULAPACK.

    Parameters
    ----------
    a : ndarray
        Coefficient matrix (n x n) stored as a full matrix. Real matrices
        should be symmetric, complex matrices should be Hermitian and
        positive-definite.

    Returns
    -------
    L : ndarray
        Lower-triangular matrix from the factorization (A = L * L^T or
        A = L * L^H).
    info : int
        0 if success, >0 if the matrix is not positive-definite.
    """
    # Ensure input is contiguous and correct dtype
    a = np.ascontiguousarray(a.copy())
    n = a.shape[0]
    lda = n

    # Prepare output array
    l_flat = a.ravel(order="C")  # Row-major flattening for NULAPACK
    info = np.zeros(1, dtype=np.int32)

    # Call appropriate NULAPACK routine based on dtype
    if np.issubdtype(a.dtype, np.floating):
        if a.dtype == np.float32:
            # Single precision real
            _nulapack.spoctrf(n, l_flat, lda, info)
        else:  # float64
            # Double precision real
            _nulapack.dpoctrf(n, l_flat, lda, info)
    elif np.issubdtype(a.dtype, np.complexfloating):
        if a.dtype == np.complex64:
            # Single precision complex
            _nulapack.cpoctrf(n, l_flat, lda, info)
        else:  # complex128
            # Double precision complex
            _nulapack.zpoctrf(n, l_flat, lda, info)
    else:
        raise TypeError(f"Unsupported array dtype: {a.dtype}")

    # Reshape flat array back to 2D row-major
    L = l_flat.reshape(n, n, order="C")  # noqa: N806

    # Only lower-triangular part is valid
    L = np.tril(L)  # noqa: N806

    return L, int(info[0])
