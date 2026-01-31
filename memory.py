import ctypes
from ctypes import c_void_p, c_size_t, c_ssize_t, c_int
import psutil
import struct

# Carrega a libc
libc = ctypes.CDLL("libc.so.6")

# Estrutura iovec
class iovec(ctypes.Structure):
    _fields_ = [
        ("iov_base", c_void_p),
        ("iov_len", c_size_t)
    ]

# Configura process_vm_readv/writev
process_vm_readv = libc.process_vm_readv
process_vm_readv.argtypes = [c_int, ctypes.POINTER(iovec), c_size_t, ctypes.POINTER(iovec), c_size_t, c_size_t]
process_vm_readv.restype = c_ssize_t

process_vm_writev = libc.process_vm_writev
process_vm_writev.argtypes = [c_int, ctypes.POINTER(iovec), c_size_t, ctypes.POINTER(iovec), c_size_t, c_size_t]
process_vm_writev.restype = c_ssize_t

class Memory:
    def __init__(self):
        self.pid = 0
        self.client_base = 0
        print("Memory manager inicializado (100% Python puro). Procurando CS 1.6...")

    def find_cs_pid(self):
        """Encontra PID e base do client.so"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'hl_linux' in proc.info['name'].lower():
                    self.pid = proc.info['pid']
                    self.client_base = self.find_client_module()
                    if self.client_base:
                        print(f"✓ Processo encontrado: PID {self.pid}")
                        print(f"✓ client.so base: 0x{self.client_base:x}")
                        return True
            except:
                continue
        return False

    def find_client_module(self):
        if not self.pid:
            return 0
        try:
            with open(f"/proc/{self.pid}/maps", "r") as f:
                for line in f:
                    if "client.so" in line:
                        addr_str = line.split('-')[0]
                        return int(addr_str, 16)
        except:
            pass
        return 0

    def read_memory(self, addr, size):
        buffer = ctypes.create_string_buffer(size)
        local = iovec(ctypes.addressof(buffer), size)
        remote = iovec(c_void_p(addr), size)

        result = process_vm_readv(self.pid, local, 1, remote, 1, 0)
        if result == size:
            return buffer.raw
        return None

    def read_uint(self, addr):
        data = self.read_memory(addr, 4)
        return struct.unpack("<I", data)[0] if data else 0

    def read_int(self, addr):
        data = self.read_memory(addr, 4)
        return struct.unpack("<i", data)[0] if data else 0

    def read_float(self, addr):
        data = self.read_memory(addr, 4)
        return struct.unpack("<f", data)[0] if data else 0.0

    def read_vec3(self, addr):
        data = self.read_memory(addr, 12)
        if data:
            return struct.unpack("<fff", data)
        return (0.0, 0.0, 0.0)

    def write_float(self, addr, value):
        data = struct.pack("<f", value)
        buffer = ctypes.create_string_buffer(data)
        local = iovec(ctypes.addressof(buffer), len(data))
        remote = iovec(c_void_p(addr), len(data))

        result = process_vm_writev(self.pid, local, 1, remote, 1, 0)
        return result == len(data)

    def write_int(self, addr, value):
        data = struct.pack("<i", value)
        buffer = ctypes.create_string_buffer(data)
        local = iovec(ctypes.addressof(buffer), len(data))
        remote = iovec(c_void_p(addr), len(data))

        result = process_vm_writev(self.pid, local, 1, remote, 1, 0)
        return result == len(data)