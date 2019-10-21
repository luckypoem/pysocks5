#encoding:utf8
from socket import socket, AF_INET, SOCK_STREAM
import time

addr = ("localhost", 12580)
sock = socket(AF_INET, SOCK_STREAM)
s = sock.connect(addr)
sock.sendall("\x05\x01\x00") # auth
sock.sendall("\x05\x01\x00\x03\x0dwww.baidu.com\x00\x50") # connect
print(sock.recv(1024))
sock.sendall("GET / HTTP/1.1\r\nHost: www.baidu.com\r\nUser-Agent: curl/7.58.0\r\n\
    Accept: */*\r\n\r\n")
ret = sock.recv(4096)
while ret:
    print(ret)
    ret = sock.recv(4096)
    if not ret:
        break
