#!coding=utf-8

import threading
import socket
import struct


def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口为9001
        s.bind(('127.0.0.1', 9001))
        # 设置监听数
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
        conn, addr = s.accept()
        # 接收数据
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    # 收到请求后的回复
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))

    while 1:
        # 申请相同大小的空间存放发送过来的文件名与文件大小信息
        fileinfo_size = struct.calcsize('128sl')
        # 接收文件名与文件大小信息
        buf = conn.recv(fileinfo_size)
        # 判断是否接收到文件头信息
        if buf:
            # 获取文件名和文件大小
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(b'\00')
            fn = fn.decode()
            print('file new name is {0}, filesize if {1}'.format(str(fn), filesize))

            recvd_size = 0  # 定义已接收文件的大小
            # 存储在该脚本所在目录下面
            fp = open('./' + str(fn), 'wb')
            print('start receiving...')

            # 将分批次传输的二进制流依次写入到文件
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print('end receive...')
        # 传输结束断开连接
        conn.close()
        break


if __name__ == "__main__":
    socket_service()
