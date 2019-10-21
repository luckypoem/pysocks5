#encoding:utf8
import sys
from socket import socket, AF_INET, SOCK_STREAM
from enum import Enum

class Result(Enum):
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

method_meaning = {
    bytes.fromhex("00"): "no auth require",
    bytes.fromhex("01"): "GSSAPI",
    bytes.fromhex("02"): "USERNAME/PASSWORD",
}
def explain_client_accept_auth_method(methods):
    for byte in methods:
        print(method_meaning.get(byte, "unknown method"))

def auth(sock):
    version = sock.recv(1)
    if version != bytes.fromhex('05'):
        print("socks version not match! got:", version)
        return Result.FAIL
    nmethods_str = sock.recv(1)
    nmethods = int(nmethods_str, 16)
    result = read_exact(sock, nmethods)
    explain_client_accept_auth_method(result) 
    #only support no password
    sock.write(bytes.fromhex("0500"))
    return Result.SUCC

def connect(sock, client_addr):
    ver = sock.recv(1)
    if version != bytes.fromhex('05'):
        print("socks version not match! got:", version)
        return Result.FAIL
    cmd = sock.recv(1)
    if cmd != bytes.fromhex('01'):
        #TODO add more cmd
        print("cmd not allow:", cmd)
        return Result.FAIL
    rsv = sock.recv(1)  # omitted
    addr_type = sock.recv(1)
    #01:ipv4 03:域名
    if addr_type != bytes.fromhex('01') or addr_type != bytes.fromhex('03'):
        print("addr_type not allow:", addr_type)
        return Result.FAIL
    if addr_type == bytes.fromhex('01'):
        ipv4_addr = read_exact(4)
    
    
def echo_handler(client_sock, client_addr):
    print("recv conn from {}".format(client_addr))
    ret = auth(client_sock)
    if ret != Result.SUCC:
        print("auth failed")
        return
    ret, remote_sock = connect(client_sock)
    if ret != Result.SUCC:
        print("connect failed")
        return
    while 1:
        msg = client_sock.recv(1024)
        if not msg:
            break
        remote_sock.sendall(msg)
    print(client_addr, "connection close")
    client_sock.close()

addr = ("localhost", 12580)
def echo_server(addr, backlog=5):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(addr)
    sock.listen(backlog)
    while 1:
        client_sock, client_addr = sock.accept()
        echo_handler(client_sock, client_addr)

if __name__ == "__main__":
    print("listen on:", addr)
    echo_server(addr)
