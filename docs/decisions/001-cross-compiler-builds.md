# ADR-0001: Build on multiple compilers as a correctness layer

Date: 2026-07-13
Status: Accepted

## Context
First cross-compiler bug found: kernels.hpp used M_PI, a POSIX extension that
GCC exposes by default but standard C++ does not define. GCC (core-cpp CI in
container) compiled silently; MSVC on Windows correctly rejected it. The
inverse (MSVC-permissive, GCC-strict) will also occur.

## Decision
core-cpp must always build on at least two compilers (MSVC + GCC). No
non-standard extensions; portable named constants instead of platform macros
(PI defined in kernels.hpp). A compile on both is treated as part of the
conformance bar alongside the 14-fixture suite.

## Consequences
Free extra correctness checking on top of the conformance suite. Slightly
stricter coding style (standard C++17 only). Catches portability rot before
it reaches the pybind11/Android builds, which will add yet more toolchains.