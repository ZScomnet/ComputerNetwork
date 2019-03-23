import socket
import argparse
from os.path import getsize, abspath

def run(host, port, file_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(file_name.encode())
        data_size = s.recv(6) # 파일사이즈 수령
        data_size.decode('utf-8')
        if int(data_size) == 0:
            print("No File In Server!!!")
            return
        else:
            with open(file_name,'wb') as f:
                try:
                    for i in range(0,int(data_size)): # 파일 사이즈만큼 write
                        data = s.recv(1)
                        f.write(data)
                except Exception as e:
                    print(e)
            print("file_name : %s" % file_name)
            print("size : %d" % getsize(abspath(file_name)))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo client -p port -i host -f file")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-i', help="host_name", required=True)
    parser.add_argument('-f', help="file_name", required=True)
    args = parser.parse_args()
    run(host=args.i, port=int(args.p), file_name=args.f)

'''
with 문을 사용하면 with 블록을 벗어나는순간 열린 객체가 자동으로 닫힘
소켓은 자동으로 연결을 끊고 파일은 자동으로 닫는다.

'''