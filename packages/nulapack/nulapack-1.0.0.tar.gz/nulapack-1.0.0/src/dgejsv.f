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
C       DGEJSV  -   Jacobi Solver for A * X = B
C     ====================================================================
C       Description:
C       ------------------------------------------------------------------
C         Iterative Jacobi solver for solving linear systems of
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
C         N         : INTEGER             -> size of the matrix (N x N)
C         A(*)      : DOUBLE PRECISION     -> flat array, row-major matrix A
C         B(N)      : DOUBLE PRECISION     -> right-hand side vector
C         X(N)      : DOUBLE PRECISION     -> input: initial guess, output: solution
C         MAX_ITER  : INTEGER             -> max number of iterations
C         TOL       : DOUBLE PRECISION    -> convergence tolerance
C         OMEGA     : DOUBLE PRECISION    -> relaxation coefficient
C         INFO      : INTEGER             -> return code:
C                                              0 = success
C                                             >0 = did not converge
C                                             <0 = illegal or zero diagonal
C     ====================================================================
      SUBROUTINE DGEJSV(N, A, B, X, MAX_ITER, TOL, OMEGA, INFO)

C   I m p l i c i t   T y p e s
C   ------------------------------------------------------------------
      IMPLICIT NONE

C   D u m m y   A r g u m e n t s
C   ------------------------------------------------------------------
      INTEGER             :: N, MAX_ITER, INFO
      DOUBLE PRECISION    :: A(*), B(N), X(N), TOL, OMEGA

C   L o c a l   V a r i a b l e s
C   ------------------------------------------------------------------
      INTEGER             :: I, J, K, INDEX
      DOUBLE PRECISION    :: X_NEW(N)
      DOUBLE PRECISION    :: S, DIFF, MAX_DIFF

C   I n i t i a l   S t a t u s
C   ------------------------------------------------------------------
      INFO = 1   ! Default: did not converge

C   M a i n   I t e r a t i o n   L o o p
C   ------------------------------------------------------------------
      DO K = 1, MAX_ITER
         DO I = 1, N
            S = 0.0D0

C           Compute sum: S = sum_{j=1}^{N, j!=i} A(i,j) * X(j)
            DO J = 1, N
               IF (J .NE. I) THEN
                  INDEX = (I - 1) * N + J
                  S = S + A(INDEX) * X(J)
               END IF
            END DO

C           Check diagonal element A(i,i)
            INDEX = (I - 1) * N + I
            IF (A(INDEX) .EQ. 0.0D0) THEN
               INFO = -I
               RETURN
            END IF

C           Jacobi update with relaxation
            X_NEW(I) = (B(I) - S) / A(INDEX)
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
            INFO = 0  ! Success
            RETURN
         END IF
      END DO

C   N o n - C o n v e r g e n c e   E x i t
C   ------------------------------------------------------------------
      RETURN
      END
