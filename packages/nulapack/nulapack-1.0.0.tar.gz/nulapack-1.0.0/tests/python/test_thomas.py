import numpy as np
from nulapack import thomas


def test_single_precision():
    a = np.array(
        [
            [10.0, -1.0, 0.0, 0.0],
            [-1.0, 11.0, -1.0, 0.0],
            [0.0, -1.0, 10.0, -1.0],
            [0.0, 0.0, -1.0, 8.0],
        ],
        dtype=np.float32,
    )
    b = np.array([6.0, 25.0, -11.0, 15.0], dtype=np.float32)

    x, info = thomas(a, b)
    assert info == 0

    assert np.allclose(
        x,
        np.array(
            [372 / 449, 1026 / 449, -311 / 449, 803 / 449],
            dtype=np.float32,
        ),
        atol=1e-5,
    )


def test_double_precision():
    a = np.array(
        [
            [10.0, -1.0, 0.0, 0.0],
            [-1.0, 11.0, -1.0, 0.0],
            [0.0, -1.0, 10.0, -1.0],
            [0.0, 0.0, -1.0, 8.0],
        ],
        dtype=np.float64,
    )
    b = np.array([6.0, 25.0, -11.0, 15.0], dtype=np.float64)

    x, info = thomas(a, b)
    assert info == 0
    assert np.allclose(
        x,
        np.array(
            [372 / 449, 1026 / 449, -311 / 449, 803 / 449],
            dtype=np.float64,
        ),
        atol=1e-12,
    )


def test_complex_float():
    a = np.array(
        [
            [10.0 + 0.0j, -1.0, 0.0, 0.0],
            [-1.0, 11.0 + 0.0j, -1.0, 0.0],
            [0.0, -1.0, 10.0 + 0.0j, -1.0],
            [0.0, 0.0, -1.0, 8.0 + 0.0j],
        ],
        dtype=np.complex64,
    )
    b = np.array([6.0 + 0.0j, 25.0 + 0.0j, -11.0 + 0.0j, 15.0 + 0.0j], dtype=np.complex64)

    x, info = thomas(a, b)
    assert info == 0

    assert np.allclose(
        x,
        np.array(
            [372 / 449, 1026 / 449, -311 / 449, 803 / 449],
            dtype=np.complex64,
        ),
        atol=1e-5,
    )


def test_complex_double():
    a = np.array(
        [
            [10.0 + 0.0j, -1.0, 0.0, 0.0],
            [-1.0, 11.0 + 0.0j, -1.0, 0.0],
            [0.0, -1.0, 10.0 + 0.0j, -1.0],
            [0.0, 0.0, -1.0, 8.0 + 0.0j],
        ],
        dtype=np.complex128,
    )
    b = np.array([6.0 + 0.0j, 25.0 + 0.0j, -11.0 + 0.0j, 15.0 + 0.0j], dtype=np.complex128)

    x, info = thomas(a, b)
    assert info == 0

    assert np.allclose(
        x,
        np.array(
            [372 / 449, 1026 / 449, -311 / 449, 803 / 449],
            dtype=np.complex128,
        ),
        atol=1e-12,
    )
