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
C       DGEGSSV  -   Gauss-Seidel Solver for A * X = B
C     ====================================================================
C       Description:
C       ------------------------------------------------------------------
C         Iterative Gauss-Seidel solver for solving linear systems of
C         equations A * X = B, where A is a square N x N matrix in
C         row-major flat array format. Double precision version.
C
C         On input:  X contains initial guess
C         On output: X contains solution
C
C         Convergence is based on maximum absolute difference per iteration.
C     ====================================================================
C       Arguments:
C       ------------------------------------------------------------------
C         N         : INTEGER            -> size of the matrix (N x N)
C         A(*)      : DOUBLE PRECISION   -> flat array, row-major matrix A
C         B(N)      : DOUBLE PRECISION   -> right-hand side vector
C         X(N)      : DOUBLE PRECISION   -> input: initial guess, output: solution
C         MAX_ITER  : INTEGER            -> max number of iterations
C         TOL       : DOUBLE PRECISION   -> convergence tolerance
C         OMEGA     : DOUBLE PRECISION   -> relaxation coefficient
C         STATUS    : INTEGER            -> return code:
C                                                 0 = success
C                                                >0 = did not converge
C                                                <0 = illegal or zero diagonal
C     ====================================================================
      SUBROUTINE DGEGSSV(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)

C   I m p l i c i t   T y p e s
C   ------------------------------------------------------------------
      IMPLICIT NONE

C   D u m m y   A r g u m e n t s
C   ------------------------------------------------------------------
      INTEGER            :: N, MAX_ITER, STATUS
      DOUBLE PRECISION   :: A(*), B(N), X(N), TOL, OMEGA

C   L o c a l   V a r i a b l e s
C   ------------------------------------------------------------------
      INTEGER            :: I, J, K, INDEX
      DOUBLE PRECISION   :: X_NEW(N)
      DOUBLE PRECISION   :: S1, S2, DIFF, MAX_DIFF

C   I n i t i a l   S t a t u s
C   ------------------------------------------------------------------
      STATUS = 1   ! Default: did not converge

C   M a i n   I t e r a t i o n   L o o p
C   ------------------------------------------------------------------
      DO K = 1, MAX_ITER
         DO I = 1, N
            S1 = 0.0D0
            S2 = 0.0D0

C           Compute sum: S1 = sum_{j=1}^{i-1} A(i,j) * X_NEW(j)
            DO J = 1, I - 1
               INDEX = (I - 1) * N + J
               S1 = S1 + A(INDEX) * X_NEW(J)
            END DO

C           Compute sum: S2 = sum_{j=i+1}^{N} A(i,j) * X(j)
            DO J = I + 1, N
               INDEX = (I - 1) * N + J
               S2 = S2 + A(INDEX) * X(J)
            END DO

C           Check diagonal element A(i,i)
            INDEX = (I - 1) * N + I
            IF (A(INDEX) .EQ. 0.0D0) THEN
               STATUS = -I
               RETURN
            END IF

C           Update X_NEW(i) with relaxation
            X_NEW(I) = (B(I) - S1 - S2) / A(INDEX)
            X_NEW(I) = X(I) + OMEGA * (X_NEW(I) - X(I))
         END DO

C        C o n v e r g e n c e   C h e c k
C        ----------------------------------------------------------------
         MAX_DIFF = 0.0D0
         DO I = 1, N
            DIFF = ABS(X_NEW(I) - X(I))
            IF (DIFF .GT. MAX_DIFF) MAX_DIFF = DIFF
            X(I) = X_NEW(I)
         END DO

         IF (MAX_DIFF .LT. TOL) THEN
            STATUS = 0  ! Success
            RETURN
         END IF
      END DO

C   N o n - C o n v e r g e n c e   E x i t
C   ------------------------------------------------------------------
      RETURN
      END
