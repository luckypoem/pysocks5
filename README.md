socks5协议实现
=============
先实现CONNECT
[rfc](https://www.ietf.org/rfc/rfc1928.txt)

交互流程
=======
认证阶段：

```
    Client->Server:
    +----+----------+----------+
    |VER | NMETHODS | METHODS  |
    +----+----------+----------+
    | 1  |    1     |  1~255   |
    +----+----------+----------+
```

VER 字段是当前协议的版本号，也就是 5； NMETHODS 字段是 METHODS 字段占用的字节数； METHODS 字段的每一个字节表示一种认证方式，表示客户端支持的全部认证方式。

	0x00: NO AUTHENTICATION REQUIRED
	0x01: GSSAPI
	0x02: USERNAME/PASSWORD
	0x03: to X’7F’ IANA ASSIGNED
	0x80: to X’FE’ RESERVED FOR PRIVATE METHODS
	0xFF: NO ACCEPTABLE METHODS

Server -> Client:

```
    +----+--------+
    |VER | METHOD |
    +----+--------+
    | 1  |   1    |
    +----+--------+
```

0x05 0x00：告诉客户端采用无认证的方式建立连接；
0x05 0xff：客户端的任意一种认证方式服务器都不支持。

连接阶段:

Client -> Server:

```
    +----+-----+-------+------+----------+----------+
    |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  |   1   |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+
    CMD 字段 command 的缩写：

    * 0x01：CONNECT 建立 TCP 连接
    * 0x02: BIND 上报反向连接地址
    * 0x03：关联 UDP 请求

    RSV 字段：保留字段，值为 0x00 ATYP 字段：address type 的缩写，取值为：

    * 0x01：IPv4        
    * 0x03：域名
    * 0x04：IPv6

    DST.ADDR 字段：destination address 的缩写，取值随 ATYP 变化：

    * ATYP == 0x01：4 个字节的 IPv4 地址
    * ATYP == 0x03：1 个字节表示域名长度，紧随其后的是对应的域名
    * ATYP == 0x04：16 个字节的 IPv6 地址
    * DST.PORT 字段：目的服务器的端口

Server -> Client:
    +----+-----+-------+------+----------+----------+
    |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  |   1   |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+
     REP 字段

    * X'00' succeeded
    * X'01' general SOCKS server failure
    * X'02' connection not allowed by ruleset
    * X'03' Network unreachable
    * X'04' Host unreachable
    * X'05' Connection refused
    * X'06' TTL expired
    * X'07' Command not supported
    * X'08' Address type not supported
    * X'09' to X'FF' unassigned
```

传输阶段：

    client -> server -> remote
    remote -> server -> client
    ...    
