"""Frozen Cub package.

This package provides tools and utilities for creating and managing
immutable (frozen) data structures in Python.
"""

from frozen_cub._internal.cli import main

__all__: list[str] = ["main"]

# Cython and my Type Checker don't get along, therefore that there why there is
# so many type:ignore comments in the codebase. Deal with it or build me a
# type checker that understands Cython. Okay?
