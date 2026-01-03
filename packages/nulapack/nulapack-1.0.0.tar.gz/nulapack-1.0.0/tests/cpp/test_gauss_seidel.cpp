#define CATCH_CONFIG_MAIN
#include <catch2/catch_all.hpp>
#include <cstdio>
#include <complex>
#include "GaussSeidel.h"

TEST_CASE("SGEGSSV - SINGLE PRECISION GAUSS-SEIDEL SOLVER", "[FLOAT32]") {
    int N = 4;
    float A[16] = {
        10.0f, -1.0f, 2.0f, 0.0f,
        -1.0f, 11.0f, -1.0f, 3.0f,
        2.0f, -1.0f, 10.0f, -1.0f,
        0.0f, 3.0f, -1.0f, 8.0f
    };
    float B[4] = {6.0f, 25.0f, -11.0f, 15.0f};
    float X[4] = {};
    int max_iter = 1000;
    float tol = 1e-4f;
    int status;

    printf("\n");
    printf("--- TEST CASE ---\n");
    printf("SGEGSSV - SINGLE PRECISION GAUSS-SEIDEL SOLVER\n");
    printf("\n");

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &status);

    for (int i = 0; i < N; i++) printf("X[%d] = %.6f\n", i, X[i]);

    REQUIRE(status == 0);
    REQUIRE_THAT(X[0], Catch::Matchers::WithinAbs(1.0f, 1e-5f));
    REQUIRE_THAT(X[1], Catch::Matchers::WithinAbs(2.0f, 1e-5f));
    REQUIRE_THAT(X[2], Catch::Matchers::WithinAbs(-1.0f, 1e-5f));
    REQUIRE_THAT(X[3], Catch::Matchers::WithinAbs(1.0f, 1e-5f));
}

TEST_CASE("DGEGSSV - DOUBLE PRECISION GAUSS-SEIDEL SOLVER", "[FLOAT64]") {
    int N = 4;
    double A[16] = {
        10.0, -1.0, 2.0, 0.0,
        -1.0, 11.0, -1.0, 3.0,
        2.0, -1.0, 10.0, -1.0,
        0.0, 3.0, -1.0, 8.0
    };
    double B[4] = {6.0, 25.0, -11.0, 15.0};
    double X[4] = {};
    int max_iter = 1000;
    double tol = 1e-10;
    int status;

    printf("\n");
    printf("--- TEST CASE ---\n");
    printf("DGEGSSV - DOUBLE PRECISION GAUSS-SEIDEL SOLVER\n");
    printf("\n");

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &status);

    for (int i = 0; i < N; i++) printf("X[%d] = %.12lf\n", i, X[i]);

    REQUIRE(status == 0);
    REQUIRE_THAT(X[0], Catch::Matchers::WithinAbs(1.0, 1e-10));
    REQUIRE_THAT(X[1], Catch::Matchers::WithinAbs(2.0, 1e-10));
    REQUIRE_THAT(X[2], Catch::Matchers::WithinAbs(-1.0, 1e-10));
    REQUIRE_THAT(X[3], Catch::Matchers::WithinAbs(1.0, 1e-10));
}

TEST_CASE("CGEGSSV - COMPLEX FLOAT GAUSS-SEIDEL SOLVER", "[COMPLEX64]") {
    using cf = std::complex<float>;
    int N = 4;
    cf A[16] = {
        {10.0f, 1.0f}, {-1.0f, 0.0f}, {2.0f, 0.0f}, {0.0f, 0.0f},
        {-1.0f, 0.0f}, {11.0f, 1.0f}, {-1.0f, 0.0f}, {3.0f, 0.0f},
        {2.0f, 0.0f}, {-1.0f, 0.0f}, {10.0f, 1.0f}, {-1.0f, 0.0f},
        {0.0f, 0.0f}, {3.0f, 0.0f}, {-1.0f, 0.0f}, {8.0f, 1.0f}
    };
    cf B[4] = { {6.0f, 1.0f}, {25.0f, 2.0f}, {-11.0f, 1.0f}, {15.0f, -1.0f} };
    cf X[4] = {};
    int max_iter = 1000;
    float tol = 1e-4f;
    int status;

    printf("\n");
    printf("--- TEST CASE ---\n");
    printf("CGEGSSV - COMPLEX FLOAT GAUSS-SEIDEL SOLVER\n");
    printf("\n");

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &status);

    for (int i = 0; i < N; i++) {
        printf("X[%d] = (%.6f, %.6f)\n", i, X[i].real(), X[i].imag());
    }

    REQUIRE(status == 0);
    REQUIRE_THAT(X[0].real(), Catch::Matchers::WithinAbs(0.995412f, 1e-5f));
    REQUIRE_THAT(X[0].imag(), Catch::Matchers::WithinAbs(-0.028752f, 1e-5f));
    REQUIRE_THAT(X[1].real(), Catch::Matchers::WithinAbs(2.018524f, 1e-5f));
    REQUIRE_THAT(X[1].imag(), Catch::Matchers::WithinAbs(0.081610f, 1e-5f));
    REQUIRE_THAT(X[2].real(), Catch::Matchers::WithinAbs(-0.982175f, 1e-5f));
    REQUIRE_THAT(X[2].imag(), Catch::Matchers::WithinAbs(0.186858f, 1e-5f));
    REQUIRE_THAT(X[3].real(), Catch::Matchers::WithinAbs(0.963693f, 1e-5f));
    REQUIRE_THAT(X[3].imag(), Catch::Matchers::WithinAbs(-0.252708f, 1e-5f));
}

TEST_CASE("ZGEGSSV - COMPLEX DOUBLE GAUSS-SEIDEL SOLVER", "[COMPLEX128]") {
    using cd = std::complex<double>;
    int N = 4;
    cd A[16] = {
        {10.0, 1.0}, {-1.0, 0.0}, {2.0, 0.0}, {0.0, 0.0},
        {-1.0, 0.0}, {11.0, 1.0}, {-1.0, 0.0}, {3.0, 0.0},
        {2.0, 0.0}, {-1.0, 0.0}, {10.0, 1.0}, {-1.0, 0.0},
        {0.0, 0.0}, {3.0, 0.0}, {-1.0, 0.0}, {8.0, 1.0}
    };
    cd B[4] = { {6.0, 1.0}, {25.0, 2.0}, {-11.0, 1.0}, {15.0, -1.0} };
    cd X[4] = {};
    int max_iter = 1000;
    double tol = 1e-12;
    int status;

    printf("\n");
    printf("--- TEST CASE ---\n");
    printf("ZGEGSSV - COMPLEX DOUBLE GAUSS-SEIDEL SOLVER\n");
    printf("\n");

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &status);

    for (int i = 0; i < N; i++) {
        printf("X[%d] = (%.12lf, %.12lf)\n", i, X[i].real(), X[i].imag());
    }

    REQUIRE(status == 0);
    REQUIRE_THAT(X[0].real(), Catch::Matchers::WithinAbs(0.995412230296, 1e-11));
    REQUIRE_THAT(X[0].imag(), Catch::Matchers::WithinAbs(-0.028751867347, 1e-11));
    REQUIRE_THAT(X[1].real(), Catch::Matchers::WithinAbs(2.018524356148, 1e-11));
    REQUIRE_THAT(X[1].imag(), Catch::Matchers::WithinAbs(0.081609612259, 1e-11));
    REQUIRE_THAT(X[2].real(), Catch::Matchers::WithinAbs(-0.982174907078, 1e-11));
    REQUIRE_THAT(X[2].imag(), Catch::Matchers::WithinAbs(0.186858027715, 1e-11));
    REQUIRE_THAT(X[3].real(), Catch::Matchers::WithinAbs(0.963693005950, 1e-11));
    REQUIRE_THAT(X[3].imag(), Catch::Matchers::WithinAbs(-0.252707976877, 1e-11));
}
