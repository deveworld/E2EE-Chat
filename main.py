import gc
import re
import sys

import SOCKET
import ENCRYPT

version = 'E2EE-WORLD-CHAT-v1.0'


def main():
    s_or_c = 0
    while not s_or_c == "S" or s_or_c == "C":
        s_or_c = input("If you're going to wait for a connection, type 's' or 'c' if you're going to connect: ")
        if s_or_c == "S" or s_or_c == "s":
            setup_server()
            return

        elif s_or_c == "C" or s_or_c == "c":
            setup_client()
            return


def setup_server(port="10000000"):
    port_re = re.compile('^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}'
                         '|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
    while not port_re.match(port):
        port = input("Please enter the port to wait for the connection: ")

    sys.stdout.write('Presetting RSA keys... ')

    prime, g = ENCRYPT.make_prime_g()
    en_data = ENCRYPT.setup(prime, g)
    del prime, g
    gc.collect()
    print("Done.")

    print("The server has started.")
    try:
        SOCKET.server(port, version, en_data)
    finally:
        print("\nTerminate Connection")


def setup_client():
    host = "notIP"
    ip_re = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).)'
                       '{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    while not ip_re.match(host):
        host = input("Please enter the IP(ipv4) of the server to connect to: ")

    port = "10000000"
    port_re = re.compile('^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}'
                         '|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
    while not port_re.match(port):
        port = input("Please enter the port of the server to connect to: ")

    print("Attempt to connect to the server.")
    try:
        SOCKET.client(host, port, version)
    finally:
        print("\nTerminate Connection")


if __name__ == "__main__":
    main()
