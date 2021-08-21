import gc
import re
import sys

import SOCKET
import ENCRYPT

version = 'E2EE-WORLD-CHAT-vBETA'


def main():
    s_or_c = 0
    while not s_or_c == "S" or s_or_c == "C":
        s_or_c = input("연결을 기다리실 거라면 'S'를 입력하시고, 연결하실거라면 'C'를 입력해주세요: ")
        if s_or_c == "S":
            setup_server()
            return

        elif s_or_c == "C":
            setup_client()
            return


def setup_server(port="10000000"):
    port_re = re.compile('^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}'
                         '|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
    while not port_re.match(port):
        port = input("연결을 기다릴 포트를 입력해주세요: ")

    sys.stdout.write('RSA 키 사전 설정중... ')

    prime, g = ENCRYPT.make_prime_g()
    en_data = ENCRYPT.setup(prime, g)
    del prime, g
    gc.collect()
    print("성공")

    print("서버가 시작되었습니다.")
    try:
        SOCKET.server(port, version, en_data)
    finally:
        print("접속이 종료되었습니다.")


def setup_client():
    host = "notIP"
    ip_re = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).)'
                       '{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    while not ip_re.match(host):
        host = input("연결할 컴퓨터의 아이피(ipv4)를 입력해주세요: ")

    port = "10000000"
    port_re = re.compile('^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}'
                         '|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
    while not port_re.match(port):
        port = input("연결할 컴퓨터의 포트를 입력해주세요: ")

    print("서버에 연결을 시도합니다.")
    try:
        SOCKET.client(host, port, version)
    finally:
        print("\n접속이 종료되었습니다.")


if __name__ == "__main__":
    main()
