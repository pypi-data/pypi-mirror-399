from glob import glob
from sys import platform
from platform import machine
import ctypes
import os


if platform == 'darwin':
    file_ext = '-arm64-*.dylib' if machine() == "arm64" else '-x86-*.dylib'
elif platform in ('win32', 'cygwin'):
    file_ext = '*-64-*.dll' if 8 == ctypes.sizeof(ctypes.c_voidp) else '*-32-*.dll'
else:
    if machine() == "aarch64":
        file_ext = '-arm64-*.so'
    elif "x86" in machine():
        file_ext = '-x86-*.so'
    else:
        file_ext = '-amd64-*.so'

root_dir = os.path.abspath(os.path.dirname(__file__))
matches = glob(f'{root_dir}/dependencies/tls-client{file_ext}')
if not matches:
    raise FileNotFoundError(f'No tls-client library found for the current platform: {platform} {machine()}')

library = ctypes.cdll.LoadLibrary(matches[0])

# extract the exposed request function from the shared package
request = library.request
request.argtypes = [ctypes.c_char_p]
request.restype = ctypes.c_char_p

freeMemory = library.freeMemory
freeMemory.argtypes = [ctypes.c_char_p]
freeMemory.restype = ctypes.c_char_p

destroySession = library.destroySession
destroySession.argtypes = [ctypes.c_char_p]
destroySession.restype = ctypes.c_char_p
