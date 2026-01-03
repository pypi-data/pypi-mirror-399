# Contributing to NULAPACK

Thank you for your interest in contributing to NULAPACK (NUmerical Linear Algebra PACKage)! We appreciate your efforts to improve this project. This document provides guidelines and instructions for contributing.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before participating in this project. We are committed to providing a welcoming and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you discover a bug, please create an issue on GitHub with the following information:

- **Title**: A clear, concise summary of the bug
- **Description**: Detailed description of the issue
- **Reproduction Steps**: Step-by-step instructions to reproduce the bug
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, compiler, version, build system used
- **Attachments**: Error messages, stack traces, or minimal reproducible examples

### Requesting Features

Feature requests are welcome! Please create an issue with:

- **Title**: A clear description of the requested feature
- **Motivation**: Why this feature would be useful
- **Proposed Implementation**: Optional suggestions on how to implement it
- **Examples**: Use cases or examples demonstrating the feature

### Submitting Code Changes

1. **Fork the Repository**: Create a personal fork on GitHub

2. **Create a Branch**: Use a descriptive branch name
   ```bash
   git checkout -b feature/routine-name-improvement
   git checkout -b fix/bug-description
   ```

3. **Follow LAPACK Naming Conventions**: All routines must follow the strict LAPACK naming convention:
   - Format: `<T><MAT><NAME><OP>` (e.g., `DGEGSSV`)
   - `<T>`: Single letter for precision (S, D, C, Z)
   - `<MAT>`: Two-letter matrix type (GE, SY, HE, PO, TR, etc.)
   - `<NAME>`: 1-2 letter initials from solver name
   - `<OP>`: 2-3 letter operation code (SV, TRF, TRS, EV, SVD, GSV, etc.)
   - No underscores, all uppercase, 6-8 characters total

   Reference: [LAPACK matrix type conventions](https://www.netlib.org/lapack/lug/node24.html)

4. **Code Style Guidelines**:
   - **Fortran**: Use fixed-form Fortran with proper indentation
     - Include descriptive header comments with routine name and purpose
     - Follow LAPACK documentation style
     - Define all variables explicitly
   - **C/C++**: Follow standard C11/C++11 conventions
     - Use meaningful variable names
     - Add comments for non-obvious logic
   - **Python**: Follow PEP 8 style guide
     - Use type hints where possible
     - Write docstrings for all functions

5. **Testing**:
   - Write tests for new functionality in the `tests/` directory
   - Ensure all existing tests pass: `pytest tests/`
   - Test with different precisions (S, D, C, Z variants where applicable)
   - Include edge cases (empty matrices, singular matrices, etc.)

6. **Documentation**:
   - Update README.md if adding new features
   - Include inline comments in code
   - Add docstrings/header comments following the existing format
   - Include mathematical references for new algorithms

7. **Commit Messages**: Write clear, descriptive commit messages
   ```
   [CATEGORY] Brief description

   Detailed explanation of what changed and why.
   Reference any related issues: Fixes #123
   ```
   Categories: FEAT (feature), FIX (bug fix), REFACTOR (code restructuring), DOCS (documentation), TEST (testing)

8. **Push and Create Pull Request**:
   ```bash
   git push origin feature/routine-name-improvement
   ```
   - Provide a clear PR description
   - Link related issues
   - Ensure CI passes

## Development Setup

### Prerequisites
- CMake 3.10+
- Fortran compiler (gfortran or ifort)
- C/C++11 compiler
- Python 3.10+
- UV
- Git

### Building from Source

```bash
# Clone the repository
git clone https://github.com/saudzahirr/NULAPACK.git
cd NULAPACK

# Setup Environment
uv venv
source .venv/bin/activate
python bin/build.py develop
```

### Build Options

```
python ./bin/build.py

usage: build.py [-h] {build, install, wheel, doxygen, develop, test, clean}
```

## Coding Standards

### Fortran Conventions

- Use 6-8 character routine names (LAPACK style)
- Include precision prefix: S (single), D (double), C (complex), Z (complex*16)
- Document arguments with type and description
- Return status via INFO parameter:
  - 0: Success/Convergence
  - <0: Invalid argument (-INFO indicates which)
  - >0: Algorithm failed (e.g., iteration count if convergence failed)

### Function Signatures

Follow LAPACK signature style:
```fortran
SUBROUTINE DGEGSSV(N, A, LDA, B, X, MAX_ITER, TOL, OMEGA, INFO)
```

Arguments should be ordered:
1. Matrix dimensions (N, M, K, etc.)
2. Matrices (A, B, C, etc.)
3. Leading dimensions (LDA, LDB, etc.)
4. Scalars (parameters)
5. Output status (INFO)

### Python Conventions

- Export public API through `__init__.py`
- Use type hints in function signatures
- Write comprehensive docstrings using NumPy style
- Validate input arrays and dimensions

## Performance Considerations

- Use row-major flat array format for Fortran interoperability
- Minimize memory allocations in tight loops
- Consider cache locality in nested loops
- Profile new code for performance regressions
- Document any limitations or performance characteristics

## Documentation

Good documentation is essential! Please include:

1. **Routine Header**: Include in Fortran files
   ```fortran
   C     ==================================================================
   C     ROUTINE NAME - Brief description
   C     ==================================================================
   C     Description: Detailed explanation
   C     Arguments: List all parameters with types and meanings
   C     ==================================================================
   ```

2. **Python Docstrings**: Use NumPy style
   ```python
   def routine(x, y, param=1.0):
       """
       Brief description.
       
       Detailed description of the routine.
       
       Parameters
       ----------
       x : ndarray
           Description of x
       y : ndarray
           Description of y
       param : float, optional
           Description of parameter
           
       Returns
       -------
       result : ndarray
           Description of result
       status : int
           0 if successful, non-zero otherwise
       """
   ```

## Review Process

- At least one maintainer review is required
- All CI checks must pass
- Tests must achieve >90% coverage for new code
- Documentation must be complete
- Code must follow project conventions

## License

By contributing to NULAPACK, you agree that your contributions will be licensed under the same GNU General Public License v3.0 (or later) as the project.

## Questions?

- Check existing issues and discussions
- Contact the maintainers

Thank you for contributing to NULAPACK! Your efforts help make numerical computing more accessible and reliable.
