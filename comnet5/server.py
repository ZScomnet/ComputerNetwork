import socket
import threading
import argparse
import time
threads = []
def socket_handler(conn,addr):
    recv_string = conn.recv(1024)
    print('Connected to : ',addr[0], addr[1])
    conn.sendall(recv_string[::-1])
    time.sleep(5)
    print('%s : Closed',addr[0])
    # 여기에 클라이언트 소켓에서 데이터를 받고, 보내는 코드 작성
    # ex) conn.recv(1024)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thread server -p port")
    parser.add_argument('-p', help = "port_number", required = True)

    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(args.p)))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        t1 = threading.Thread(target=socket_handler,name="[Thread 1]",args=(conn,addr))
        t1.daemon = True
        t1.start()
        t1.join()
        # 여기에 socket.accept 후 리턴받은 클라이언트 소켓으로 스레드를 생성하는 코드 작성

    server.close()
