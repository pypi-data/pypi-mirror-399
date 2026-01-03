C     ====================================================================
C     This file is part of NULAPACK - NUmerical Linear Algebra PACKage
C
C     Copyright (C) 2025  Saud Zahir
C
C     NULAPACK is free software: you can redistribute it and/or modify
C     it under the terms of the GNU General Public License as published by
C     the Free Software Foundation, either version 3 of the License, or
C     (at your option) any later version.
C
C     NULAPACK is distributed in the hope that it will be useful,
C     but WITHOUT ANY WARRANTY; without even the implied warranty of
C     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
C     GNU General Public License for more details.
C
C     You should have received a copy of the GNU General Public License
C     along with NULAPACK.  If not, see <https://www.gnu.org/licenses/>.
C
C     ====================================================================
C       CPOCTRF  -  Cholesky Factorization for A = L * L^T (complex single)
C     ====================================================================
C       Description:
C       ------------------------------------------------------------------
C         Computes the Cholesky factorization of a complex Hermitian
C         positive-definite matrix A stored in a flat row-major array.
C         The lower-triangular matrix L overwrites the lower triangle of A.
C
C         On output: A contains L in the lower triangle, upper triangle is
C         not referenced.
C
C     ====================================================================
C       Arguments:
C       ------------------------------------------------------------------
C         N    : INTEGER       -> order of the matrix
C         A(*) : COMPLEX      -> flat row-major matrix, size (LDA*N)
C         LDA  : INTEGER       -> leading dimension of A (usually N)
C         INFO : INTEGER       -> return code:
C                                0 = success
C                               <0 = illegal argument
C                               >0 = matrix not positive definite
C     ====================================================================
      SUBROUTINE CPOCTRF(N, A, LDA, INFO)

C   Implicit types
C   ------------------------------------------------------------------
      IMPLICIT NONE

C   Dummy arguments
C   ------------------------------------------------------------------
      INTEGER       :: N, LDA, INFO
      COMPLEX       :: A(*)

C   Local variables
C   ------------------------------------------------------------------
      INTEGER       :: I, J, K, INDEX
      COMPLEX       :: SUM

C   Initialize
C   ------------------------------------------------------------------
      INFO = 0

C   Main loop over rows
C   ------------------------------------------------------------------
      DO I = 1, N

C       Compute diagonal element L(I,I)
         SUM = (0.0, 0.0)
         DO K = 1, I-1
            INDEX = (I-1)*LDA + K
            SUM = SUM + A(INDEX)*CONJG(A(INDEX))
         END DO

         INDEX = (I-1)*LDA + I
         IF (REAL(A(INDEX)) - REAL(SUM) .LE. 0.0) THEN
            INFO = I
            RETURN
         END IF
         A(INDEX) = CSQRT(A(INDEX) - SUM)

C       Compute off-diagonal elements L(J,I), J = I+1:N
         DO J = I+1, N
            SUM = (0.0, 0.0)
            DO K = 1, I-1
               SUM = SUM + A((J-1)*LDA + K) * CONJG(A((I-1)*LDA + K))
            END DO
            INDEX = (J-1)*LDA + I
            A(INDEX) = (A(INDEX) - SUM)/A((I-1)*LDA + I)
         END DO

      END DO

C   Successful exit
C   ------------------------------------------------------------------
      RETURN
      END
