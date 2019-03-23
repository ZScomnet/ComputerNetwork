import socket
import argparse
import glob
import os.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_server(port,DIR):
    host = ''
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen(1)
        conn, addr = s.accept() # 클라이언트가 연결을 시도할 때 까지 여기서 대기
        file_name = conn.recv(30) # 파일 이름 recv
        file_name_in_server = os.path.join(DIR, file_name.decode('utf-8')) # server.py로 부터  파일 경로
        open_directory = os.path.join(BASE_DIR)
        open_directory += '\\' ## C:부터 파일경로
        file_list = glob.glob("**/*", recursive=True)
        for cnt in range(0, len(file_list)):
            if file_list[cnt] == file_name_in_server:
                break
        if file_name_in_server == file_list[cnt]:
            print("Send %s" % (file_name_in_server))  # 파일 3.전송
            with open(open_directory + file_name_in_server, 'rb') as f:
                try:
                    file = f.read(os.path.getsize(file_list[cnt]))
                    file_transferred = os.path.getsize(file_list[cnt])
                    conn.send(str(os.path.getsize(file_list[cnt])).encode()) # 파일 사이즈 전송
                    conn.sendall(file) # 파일 전송
                except Excpetion as e:
                    print(e)
                print("Send Complete! Size : %d" % (file_transferred))
        else:
            print("No File in Server!!")
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port -d directory")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-d', help="directory", required=True)

    args = parser.parse_args()
    run_server(port=int(args.p),DIR=args.d)
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
socket(도메인,유형)
도메인은 2종류가 존재(family)
AF_INET : 서버와 클라이언트가 서로 다른기계에 있을수 있음. 대다수 이거 사용
AF_UNIX : 서버와 클라이언트가 서로 같은기계에 있음.

유형
SOCK_STREAM : 스트림 연결(TCP), 신뢰성 좋고, 전송 가능 크기 가변적
SOCK_DGRAM : 데이터 그램 연결(UDP), 신뢰성 나쁨, 속도 빠름, 전송 가능 크기 정해져있음

bind((HOST,PORT)) s.bind(...) - 서버에서만 사용
이 메소드는 소켓을 HOST의 PORT에 연결
listen(n)
연결을 원하는 클라이언트가 대기할 수 있는 큐의 크기 1이상 이며 보통 5를 갖는다.
accept()
접속 개시
recv(burfsize)
소켓으로부터 데이터를 읽어온다. 한번에 읽어드리는 최데 데이터 양은 burfsize
send(string)
데이터를 소켓에 쓴다.값은 클라이언트로 전달
close()
소켓 닫음
'''