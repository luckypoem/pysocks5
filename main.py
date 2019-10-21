#!/usb/bin/python3 coding:utf8
"""
socks5 server
"""

import sys
import traceback
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
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
    b'\x00': "no auth require",
    b'\x01': "GSSAPI",
    b'\x02': "USERNAME/PASSWORD",
}
def explain_client_accept_auth_method(methods):
    for byte in methods:
        print("bytes:", byte)
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
    remote_sock = socket(AF_INET, SOCK_STREAM)
    print("remote_host:", remote_host, "port:", port)
    remote_sock.connect((remote_host, port))
    return Result.SUCC, remote_sock

def echo_handler(client_sock, client_addr):
    print("recv conn from {}".format(client_addr))
    ret = auth(client_sock)
    if ret != Result.SUCC:
        print("auth failed")
        return
    ret, remote_sock = connect(client_sock, client_addr)
    if ret != Result.SUCC:
        print("connect failed")
        return
    while 1:
        try:
            req = client_sock.recv(4096)
            if req:
                remote_sock.sendall(req)
            resp = remote_sock.recv(4096)
            client_sock.sendall(resp)
        except ConnectionResetError:
            traceback.print_tb(sys.exc_info()[2])
            print("ConnectionResetError:", client_addr)
            break
        except:
            traceback.print_tb(sys.exc_info()[2])
            print("Unexpected error:", client_addr)
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
