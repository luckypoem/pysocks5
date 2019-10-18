#encoding:utf8
from socket import socket, AF_INET, SOCK_STREAM

addr = ("localhost", 12580)

def echo_handler(client_sock, client_addr):
    print("recv conn from {}".format(client_addr))
    while 1:
        msg = client_sock.recv(1024)
        if not msg:
            break
        client_sock.sendall(msg)
    print(client_addr, "connection close")
    client_sock.close()

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
