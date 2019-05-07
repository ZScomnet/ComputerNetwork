import socket
import argparse

def run_server(port=4000):
    host = ''
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen(1)

        conn, addr = s.accept()
        msg = conn.recv(1024)
        print(msg.decode())
        conn.sendall(msg[::-1])
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port")
    parser.add_argument('-p', help="port_number", required=True)

    args = parser.parse_args()
    run_server(port=int(args.p))
'''
if __name__ == '__main__' 
이 조건문은 이 모듈이 직접 실행되는 경우에만 작동.
즉 server.py를 직접 run 하면 조건 성립

argparse - 파이썬 표준 라이브러리에서 권장하는 명령행 파싱 모듈
기본적으로 -h 기능은 내장되어 있음. 설정시 오류 출력
add_argument() : 이 메소드는 프로그램이 받고 싶은 명령행 옵션을 지정
parse_args() : 이 메소드는 실제로 지정된 옵션으로부터 온 데이터를 돌려줌
add_argument('-o', help="port_number")
ㄴ -o 명령행 지정, -h 입력시 port_number 출력 

'''