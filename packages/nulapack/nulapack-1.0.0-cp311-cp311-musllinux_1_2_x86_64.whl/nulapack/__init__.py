from importlib.metadata import PackageNotFoundError, version

from .cholesky import cholesky
from .gauss_seidel import gauss_seidel
from .jacobi import jacobi
from .thomas import thomas


try:
    __version__ = version("nulapack")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ["__version__", "cholesky", "gauss_seidel", "jacobi", "thomas"]
