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
C       CGTTSV  -  Thomas Algorithm for (tridiagonal system)
C     ====================================================================
C       Description:
C       ------------------------------------------------------------------
C         Direct solver for tridiagonal linear systems A * X = B using
C         the Thomas algorithm.  A is supplied as a FULL N x N matrix in
C         flat row-major storage and is overwritten during computation.
C
C         On output: X contains the solution vector.
C
C         No pivoting is performed. Zero diagonal entries produce failure.
C     ====================================================================
C       Arguments:
C       ------------------------------------------------------------------
C         N      : INTEGER            -> matrix size (N x N)
C         A(*)   : COMPLEX            -> flat row-major matrix A (modified)
C         B(N)   : COMPLEX            -> right-hand side (modified)
C         X(N)   : COMPLEX            -> solution vector (output)
C         INFO   : INTEGER            -> return code:
C                                           0 = success
C                                          <0 = zero diagonal detected
C     ====================================================================
      SUBROUTINE CGTTSV(N, A, B, X, INFO)

C   I m p l i c i t   T y p e s
C   ------------------------------------------------------------------
      IMPLICIT NONE

C   D u m m y   A r g u m e n t s
C   ------------------------------------------------------------------
      INTEGER            :: N, INFO
      COMPLEX            :: A(*), B(N), X(N)

C   L o c a l   V a r i a b l e s
C   ------------------------------------------------------------------
      INTEGER            :: I, INDEX_D, INDEX_L, INDEX_U
      COMPLEX            :: FACT

C   I n i t i a l   S t a t u s
C   ------------------------------------------------------------------
      INFO = 0

C   F o r w a r d   E l i m i n a t i o n
C   ------------------------------------------------------------------
      DO I = 2, N

C        Compute indices in flat row-major layout
         INDEX_L = (I-1) * N + (I-1)
         INDEX_D = (I-2) * N + (I-1)
         INDEX_U = (I-2) * N + I

C        Check previous diagonal
         IF (A(INDEX_D) .EQ. (0.0,0.0)) THEN
            INFO = -(I-1)
            RETURN
         END IF

         FACT = A(INDEX_L) / A(INDEX_D)

C        Update diagonal A(I,I)
         INDEX_D = (I-1) * N + I
         A(INDEX_D) = A(INDEX_D) - FACT * A(INDEX_U)

C        Update RHS B(I)
         B(I) = B(I) - FACT * B(I-1)

C        Check new diagonal
         IF (A(INDEX_D) .EQ. (0.0,0.0)) THEN
            INFO = -I
            RETURN
         END IF
      END DO

C   B a c k w a r d   S u b s t i t u t i o n
C   ------------------------------------------------------------------
      INDEX_D = (N-1) * N + N
      X(N) = B(N) / A(INDEX_D)

      DO I = N-1, 1, -1
         INDEX_D = (I-1) * N + I
         INDEX_U = (I-1) * N + (I+1)
         X(I) = (B(I) - A(INDEX_U) * X(I+1)) / A(INDEX_D)
      END DO

C   S u c c e s s
C   ------------------------------------------------------------------
      RETURN
      END
