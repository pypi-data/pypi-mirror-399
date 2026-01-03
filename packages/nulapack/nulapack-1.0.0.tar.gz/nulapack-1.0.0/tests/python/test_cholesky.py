import numpy as np
from nulapack import cholesky


def test_single_precision():
    a = np.array(
        [
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0],
        ],
        dtype=np.float32,
    )

    L, info = cholesky(a)  # noqa: N806
    assert info == 0

    # A ≈ L @ L.T
    assert np.allclose(a, L @ L.T, atol=1e-5)


def test_double_precision():
    a = np.array(
        [
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0],
        ],
        dtype=np.float64,
    )

    L, info = cholesky(a)  # noqa: N806
    assert info == 0

    # A ≈ L @ L.T
    assert np.allclose(a, L @ L.T, atol=1e-5)


def test_complex_float():
    a = np.array(
        [
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0],
        ],
        dtype=np.complex64,
    )

    L, info = cholesky(a)  # noqa: N806
    assert info == 0

    # A ≈ L @ L.H
    assert np.allclose(a, L @ L.conj().T, atol=1e-5)


def test_complex_double():
    a = np.array(
        [
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0],
        ],
        dtype=np.complex128,
    )

    L, info = cholesky(a)  # noqa: N806
    assert info == 0

    # A ≈ L @ L.H
    assert np.allclose(a, L @ L.conj().T, atol=1e-5)
