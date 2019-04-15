import socket
import threading
import argparse
import time
threads = []
def socket_handler(conn):
    host = conn.recv(1024).decode('utf-8')
    port = conn.recv(1024).decode('utf-8')
    print('Connected to : ', host, ':', port)
    # 여기에 클라이언트 소켓에서 데이터를 받고, 보내는 코드 작성
    # ex) conn.recv(1024)
def msg_send(conn):
    while True:
        send_msg = input()
        conn.sendall(send_msg.encode())

def msg_recv(conn,addr):
    while True:
        recv_msg = conn.recv(1024)
        print('From : ',addr[0],':',addr[1],'   ',recv_msg.decode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thread server -p port")
    parser.add_argument('-p', help = "port_number", required = True)

    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(args.p)))
    server.listen(5)
    conn, addr = server.accept()
    socket_handler(conn)
    sending_message = threading.Thread(target=msg_send,args=(conn,))
    receive_message = threading.Thread(target=msg_recv,args=(conn,addr))

    sending_message.start()
    receive_message.start()
    while True:
        if False:
            sending_message.join()
            receive_message.join()


        # 여기에 socket.accept 후 리턴받은 클라이언트 소켓으로 스레드를 생성하는 코드 작성

    server.close()
