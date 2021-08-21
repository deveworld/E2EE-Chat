import gc
import sys
import time
import socket
import hashlib
import threading

import ENCRYPT


def start_thread(sock, keys):
    sender = threading.Thread(target=send, args=(sock, keys[1], keys[0]))
    sender.daemon = True
    receiver = threading.Thread(target=receive, args=(sock, keys[2], keys[0]))
    receiver.daemon = True

    sender.start()
    receiver.start()

    return sender, receiver


def packet_handler(data):
    data = str(data)
    if '|||' in data:
        data_type = False
    else:  # elif '|/|' in data:
        data_type = True

    if not data_type:
        data = data.replace('|||', '')
    else:
        data = data.replace('|/|', '')

    return data_type, data


def get_int(sock):
    data = sock.recv(2048).decode('utf-8')
    if data.isdecimal():
        sock.send('100'.encode('utf-8'))
        data = int(data)
        return data
    else:
        sock.send('300'.encode('utf-8'))
        sock.close()
        return False


def receive(sock, d, n):
    data = ''
    size_data = ''
    while True:
        try:
            receive_data = sock.recv(1)
        except ConnectionResetError:
            break
        if not receive_data:
            break
        else:
            receive_data = str(receive_data.decode('utf-8'))

        if receive_data == ":":
            receive_data = sock.recv(int(size_data)).decode('utf-8')
            size_data = ''
            if ('|||' in receive_data) or ('|/|' in receive_data):
                receive_data = packet_handler(receive_data)
                data += ENCRYPT.decrypt(receive_data[1], d, n)
                if receive_data[0]:
                    sys.stdout.write('\r상대방: %s\nMe: ' % data)
                    data = ''
                else:
                    continue
            else:
                receive_data = ENCRYPT.decrypt(receive_data, d, n)
                sys.stdout.write('\r상대방: %s\nMe: ' % receive_data)
        else:
            size_data += receive_data


def send(sock, e, n):
    while True:
        try:
            inp = input('Me: ')
        except EOFError:
            break
        if inp == '':
            continue
        send_data = ENCRYPT.encrypt(inp, e, n)
        if 1 < len(send_data):
            for i in range(len(send_data) - 1):
                sock.send((str(len(send_data[i].encode('utf-8')) + 3) + ':|||' + send_data[i]).encode('utf-8'))
            last = len(send_data) - 1
            sock.send((str(len(send_data[last].encode('utf-8')) + 3) + ':|/|' + send_data[last]).encode('utf-8'))
        else:
            sock.send((str(len(send_data[0].encode('utf-8'))) + ':' + send_data[0]).encode('utf-8'))


def make_private_key(my_en_data, other_en_data, password_org):
    try:
        key = pow(other_en_data, my_en_data[2], my_en_data[1])
        n, e, d = ENCRYPT.make_keys(key, password_org)
        del key
        gc.collect()
    except Exception as e:
        print("암호화 오류: ", e)
        return False
    else:
        return n, e, d


def server(port, version, en_data):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', int(port)))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()
    print('연결됨: ', address)

    # This E2EE-CHAT PROTOCOL
    #
    # 1: RECEIVE HASHED PASSWORD
    # 100 OK    -> RIGHT
    # 300 WRONG     -> WRONG PASSWORD
    password_org = input("비밀번호를 입력해주세요: ")
    password = hashlib.sha256(
        (hashlib.sha256(str(int(port) ** 2).encode('utf8')).hexdigest() + password_org).encode('utf8')
    ).hexdigest()
    if client_socket.recv(2048).decode('utf-8') == password:
        client_socket.send('100'.encode('utf-8'))
    else:
        print("비밀번호 틀림 ")
        client_socket.send('300'.encode('utf-8'))
        client_socket.close()
        return

    # 2: SEND PRIME
    # 100 OK    -> Ok
    client_socket.send(str(en_data[1]).encode('utf-8'))
    if client_socket.recv(2048).decode('utf-8') != '100':
        client_socket.close()
        return

    # 3: SEND G
    # 100 OK    -> Ok
    client_socket.send(str(en_data[3]).encode('utf-8'))
    if client_socket.recv(2048).decode('utf-8') != '100':
        client_socket.close()
        return

    # 4: RECEIVE VERSION
    # 100 OK    -> Approved
    # 200 Not Matched Version   -> not approved
    if client_socket.recv(2048).decode('utf-8') == version:
        client_socket.send('100'.encode('utf-8'))
    else:
        print("버전이 호환되지 않음")
        client_socket.send('200'.encode('utf-8'))
        client_socket.close()
        return

    # 5: RECEIVE ENCRYPTED DATA
    # 100 OK    -> Server received
    # 300 WRONG     -> Data is not valid
    client_en_data = get_int(client_socket)
    if not client_socket:
        return

    # 6: SEND ENCRYPTED DATA (make private key)
    # 100 OK    -> Success make private key
    # 300 WRONG     -> Data is not valid
    client_socket.send(str(en_data[0]).encode('utf-8'))
    keys = make_private_key(en_data, client_en_data, password_org)
    del client_en_data, en_data
    gc.collect()
    if client_socket.recv(2048).decode('utf-8') != '100':
        client_socket.close()
        return

    # 7: SEND SERVER STATE
    # 100 OK    -> Success make private key
    # 300 WRONG     -> Data is not valid
    if not keys:
        client_socket.send('300'.encode('utf-8'))
        client_socket.close()
        return
    else:
        client_socket.send('100'.encode('utf-8'))

    # 8: VALIDATE PUBLIC KEY HASH
    # 100 OK    -> RIGHT KEY
    # 300 WRONG     -> WRONG KEY
    if client_socket.recv(2048).decode('utf-8') == hashlib.sha256(str(keys[0]).encode('utf-8')).hexdigest():
        client_socket.send('100'.encode('utf-8'))
    else:
        client_socket.send('300'.encode('utf-8'))

    # 9: SEND START TALK
    # 100 OK    -> READY
    client_socket.send('100'.encode('utf-8'))
    if client_socket.recv(2048).decode('utf-8') != '100':
        print("알 수 없는 오류")
        client_socket.close()
        return

    print("----------채팅 시작----------")
    thread = start_thread(client_socket, keys)
    try:
        while thread[0].is_alive() and thread[1].is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        return


def client(host, port, version):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, int(port)))
    except Exception as e:
        print('연결 오류: ', e)
        return
    else:
        # This E2EE-CHAT PROTOCOL
        #
        # 1: SEND HASHED PASSWORD
        # 100 OK    -> RIGHT
        # 300 WRONG     -> WRONG PASSWORD
        password_org = input("비밀번호를 입력해주세요: ")
        password = hashlib.sha256(
            (hashlib.sha256(str(int(port) ** 2).encode('utf8')).hexdigest() + password_org).encode('utf8')
        ).hexdigest()
        client_socket.send(password.encode('utf-8'))
        if client_socket.recv(2048).decode('utf-8') != '100':
            print("비밀번호 틀림")
            client_socket.close()
            return

        # 2: RECEIVE PRIME
        # 100 OK    -> Ok
        prime = get_int(client_socket)
        if not client_socket:
            return

        # 3: RECEIVE G
        # 100 OK    -> Ok
        g = get_int(client_socket)
        if not client_socket:
            return

        en_data = ENCRYPT.setup(prime, g)
        del prime, g
        gc.collect()

        # 4: SEND VERSION
        # 100 OK    -> Approved
        # 200 Not Matched Version   -> not approved
        client_socket.send(version.encode('utf-8'))
        received_data = client_socket.recv(2048).decode('utf-8')
        if received_data == "200":
            print("버전이 호환되지 않음")
            client_socket.close()
            return
        elif received_data != "100":
            client_socket.close()
            return

        # 5: SEND ENCRYPTED DATA
        # 100 OK    -> Server received
        # 300 WRONG     -> Data is not valid
        client_socket.send(str(en_data[0]).encode('utf-8'))
        if client_socket.recv(2048).decode('utf-8') != "100":
            client_socket.close()
            return

        # 6: RECEIVE SERVER'S ENCRYPTED DATA
        # 100 OK    -> Success make private key
        # 300 WRONG     -> Data is not valid
        server_en_data = int(client_socket.recv(2048).decode('utf-8'))
        keys = make_private_key(en_data, server_en_data, password_org)
        del server_en_data, en_data
        gc.collect()
        if not keys:
            client_socket.send('300'.encode('utf-8'))
            client_socket.close()
            return
        else:
            client_socket.send('100'.encode('utf-8'))

        # 7: RECEIVE SERVER STATE
        # 100 OK    -> Success make private key
        # 300 WRONG     -> Data is not valid
        if client_socket.recv(2048).decode('utf-8') != "100":
            client_socket.close()
            return

        # 8: SEND PUBLIC KEY HASH
        # 100 OK    -> RIGHT KEY
        # 300 WRONG     -> WRONG KEY
        client_socket.send(hashlib.sha256(str(keys[0]).encode('utf-8')).hexdigest().encode('utf-8'))
        if client_socket.recv(2048).decode('utf-8') != "100":
            client_socket.close()
            return

        # 9: SEND START TALK
        # 100 OK    -> READY
        if client_socket.recv(2048).decode('utf-8') != "100":
            client_socket.close()
            return
        else:
            client_socket.send('100'.encode('utf-8'))

        print("----------채팅 시작----------")
        thread = start_thread(client_socket, keys)
        try:
            while thread[0].is_alive() and thread[1].is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            return
