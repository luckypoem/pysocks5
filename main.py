#!/usb/bin/python3 coding:utf8
"""
socks5 server
"""

import sys
import traceback
import struct
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from enum import Enum
import ipaddress
import struct

class Result(Enum):
    """
    indicate succ or fail
    """
    SUCC = 0
    FAIL = 1

def read_exact(sock, size):
    result = sock.recv(size)
    len_result = len(result)
    while len_result < size:
        new_result = sock.recv(size - len_result)
        result = result + new_result
        len_result = len(result)
    return result

METHOD_MEANING = {
    0: "no auth require",
    1: "GSSAPI",
    2: "USERNAME/PASSWORD",
}
def explain_client_accept_auth_method(methods):
    for byte in methods:
        print(METHOD_MEANING.get(byte, "unknown method"))

def auth(sock):
    version = sock.recv(1)
    if version != b"\x05":
        print("socks version not match! got:", version)
        return Result.FAIL
    nmethods_str = sock.recv(1)
    nmethods = ord(nmethods_str)
    result = read_exact(sock, nmethods)
    explain_client_accept_auth_method(result)
    #only support no password
    sock.sendall("\x05\x00".encode("utf8"))
    print("auth succ")
    return Result.SUCC

def connect(sock, client_addr):
    ver = sock.recv(1)
    if ver != b'\x05':
        print("socks version not match! got:", ver)
        return Result.FAIL
    cmd = sock.recv(1)
    if cmd != b'\x01':
        #TODO add more cmd
        print("cmd not allow:", cmd)
        return Result.FAIL
    _ = sock.recv(1)  # omitted
    addr_type = sock.recv(1)
    #01:ipv4 03:域名
    if addr_type != b'\x01' and addr_type != b'\x03':
        print("addr_type not allow:", addr_type)
        return Result.FAIL
    if addr_type == b'\x01':
        ipv4_addr = read_exact(sock, 4)
        remote_host = str(ipaddress.IPv4Address(ipv4_addr))
    elif addr_type == b'\x03':
        addr_len = read_exact(sock, 1)
        remote_host = read_exact(sock, ord(addr_len))
    port_str = read_exact(sock, 2)
    port = struct.unpack(">H", port_str)[0]
    print("remote_host:", remote_host, "port:", port)
    remote_sock = socket(AF_INET, SOCK_STREAM)
    remote_sock.connect((remote_host, port))
    server_addr, server_port = remote_sock.getsockname()
    server_addr_bytes = ipaddress.IPv4Address(server_addr).packed
    #TODO add more resp to client
    sock.sendall(b"\x05\x00\x00\x01")
    sock.sendall(server_addr_bytes)
    sock.sendall(struct.pack(">H", server_port))
    return Result.SUCC, remote_sock

def try_read_to_timeout(sock, size=4096):
    ret = None
    try:
        ret = sock.recv(size)
    except (ConnectionResetError, BlockingIOError, timeout) as e:
        pass
    except:
        raise
    return ret

def echo_handler(client_sock, client_addr):
    print("recv conn from {}".format(client_addr))
    ret = auth(client_sock)
    if ret != Result.SUCC:
        print("auth failed")
        return ret
    ret, remote_sock = connect(client_sock, client_addr)
    if ret != Result.SUCC:
        print("connect failed")
        return ret
    client_sock.settimeout(0.1)
    remote_sock.settimeout(0.1)
    while 1:
        try:
            req = try_read_to_timeout(client_sock)
            if req:
                remote_sock.sendall(req)
            resp = try_read_to_timeout(remote_sock)
            if resp:
                client_sock.sendall(resp)
        except:
            print("while exception")
            exc_info = sys.exc_info()
            traceback.print_tb(exc_info[2])
            print("Unexpected error:", exc_info[0], exc_info[1], client_addr)
            break
    print(client_addr, "connection close")
    client_sock.close()
    if remote_sock:
        remote_sock.close()

def echo_server(addr, backlog=5):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(backlog)
    while 1:
        client_sock, client_addr = sock.accept()
        echo_handler(client_sock, client_addr)

ADDR = ("localhost", 12580)
if __name__ == "__main__":
    print("listen on:", ADDR)
    echo_server(ADDR)
