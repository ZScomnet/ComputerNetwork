import socket
import argparse
import threading


def send_msg(s):
    while True:
        send_message = input()
        s.sendall(send_message.encode())
def recv_msg(s):
    while True:
        recv_message = s.recv(1024)
        print('From Server : ',recv_message.decode('utf-8'))

def run(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print('Connect Complete!!')
        s.sendall(host.encode())
        s.sendall(str(port).encode())
        sending_message = threading.Thread(target=send_msg,args=(s,))
        receive_message = threading.Thread(target=recv_msg,args=(s,))
        sending_message.start()
        receive_message.start()
        while True:
            if False:
                sending_message.join()
                receive_message.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo client -p port -i host")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-i', help="host_name", required=True)

    args = parser.parse_args()
    run(host=args.i, port=int(args.p))