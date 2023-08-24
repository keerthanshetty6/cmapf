"""
MAPF utilities for clingo written in C++.
"""

from clingo.control import Control
from ._cmapf import lib as _lib, ffi as _ffi

__all__ = ["version", "add_sp_length", "add_reachable"]


def version():
    """
    The CMAPF version number.
    """
    p_major = _ffi.new("int*")
    p_minor = _ffi.new("int*")
    p_revision = _ffi.new("int*")
    _lib.cmapf_version(p_major, p_minor, p_revision)
    return p_major[0], p_minor[0], p_revision[0]


def add_sp_length(ctl: Control):
    """
    Add shortest paths.
    """
    _lib.cmapf_compute_sp_length(_ffi.cast("clingo_control_t*", ctl._rep))


def add_reachable(ctl: Control, delta: int):
    """
    Add reachable locations based on shortest paths.
    """
    _lib.cmapf_compute_reachable(_ffi.cast("clingo_control_t*", ctl._rep), delta)


__version__ = ".".join(str(num) for num in version())
