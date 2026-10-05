import ctypes
import os
import platform

import binaryninja
from binaryninja import _binaryninjacore as core
from binaryninja.log import log_error, log_info

ARCH_NAME = 'LoongArch64'
_lib = None


def _already_registered():
    try:
        binaryninja.Architecture[ARCH_NAME]
        return True
    except KeyError:
        return False


def _load():
    global _lib
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        log_error('%s: the native plugin only supports Linux x86-64. If you still get this error open a issue on my github : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/issues' % ARCH_NAME)
        return
    if _already_registered():
        log_info('%s: architecture already registered, the bundled native plugin is not loaded. If you still get this error open a issue on my (thanks ;-) !!!)github : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/issues' % ARCH_NAME)
        return
    abi = core.BNGetCurrentCoreABIVersion()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'native', 'abi%d' % abi, 'libarch_la64.so')
    if not os.path.isfile(path):
        log_error('%s: no prebuilt native plugin for core ABI %d, build it from source. If If you still get this error open a issue on my (thanks ;-) !!!)github : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/issues' % (ARCH_NAME, abi))
        return
    try:
        lib = ctypes.CDLL(path)
    except OSError as e:
        log_error('%s: could not load %s: %s hope this helps. If not i would like you to visit my github-issues and do a issue for a bug fix. : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/issues' % (ARCH_NAME, path, e))
        return
    lib.CorePluginABIVersion.restype = ctypes.c_uint32
    lib.CorePluginInit.restype = ctypes.c_bool
    if lib.CorePluginABIVersion() != abi:
        log_error('%s: %s was built for a different core ABI. You can try to build a version urself, for a newer ABI via the tools folder on my github : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/tree/main/tools' % (ARCH_NAME, path))
        return
    if not lib.CorePluginInit():
        log_error('%s: native plugin initialization failed. If this error keeps popping up i would like you to open a issue on my github : https://github.com/noah0x1/LoongArch64-Binary-Ninja-Binja-Plug-in/issues' % ARCH_NAME)
        return
    _lib = lib


_load()
