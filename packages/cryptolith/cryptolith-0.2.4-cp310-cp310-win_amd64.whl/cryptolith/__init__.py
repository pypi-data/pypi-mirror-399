
# Cryptolith Self-Protection Layer
try:
    from . import cryptolith_runtime
    cryptolith_runtime.runtime_init(vm_map={'BIN_ADD': 51, 'BIN_DIV': 206, 'BIN_MUL': 234, 'BIN_SUB': 45, 'BUILD_DICT': 129, 'BUILD_LIST': 163, 'BUILD_STRING': 113, 'CALL': 224, 'COMPARE': 168, 'JUMP': 190, 'JUMP_IF_FALSE': 196, 'LOAD_ATTR': 53, 'LOAD_CONST': 4, 'LOAD_NAME': 164, 'POP_TOP': 128, 'RETURN': 140, 'STORE_ATTR': 47, 'STORE_NAME': 101})
except ImportError:
    pass
import sys as _obs_sys
import os as _obs_os

def _junk_func():
    pass
import base64
yMMhsnICsu = base64.b64decode('/l0RfrimRy6Jo4tTh7uJPaU3sRe+4I79TtUcT+dBjBM=')

def rzYOzxJWtI(i):
    d = base64.b64decode(GMTcQbxzwM[i])
    return bytes([b ^ yMMhsnICsu[j % len(yMMhsnICsu)] for j, b in enumerate(d)]).decode('utf-8')
GMTcQbxzwM = []
from .runtime import secure_open as pkzWUAoUQR, secure_load_json as WDRGcSsRtS