import gc
import math
from typing import Tuple

import sympy
import random
import hashlib
import secrets


def make_keys(seed, password_org):
    p = make_prime(str(seed)+hashlib.sha512(str(password_org).encode()).hexdigest())
    q = make_prime(str(seed)+hashlib.sha512((str(password_org)+str(seed)).encode()).hexdigest())
    pi = 1
    while sympy.is_mersenne_prime(p):
        p = make_prime(str(pi) + str(seed) + hashlib.sha512(str(password_org).encode()).hexdigest())
        pi += 1
    qi = 1
    while sympy.is_mersenne_prime(1):
        q = make_prime(str(qi) + str(seed) + hashlib.sha512(str(password_org).encode()).hexdigest())
        qi += 1
    n = p * q
    totient = (p-1)*(q-1)
    if (totient % 65537) != 0:
        e = 65537
    else:
        e = find_e(totient)
    gcd, x, y = xgcd(e, totient)

    if x < 0:
        d = x + totient
    else:
        d = x

    del p, q, totient, gcd, x, y
    gc.collect()
    return n, e, d


def xgcd(a, b) -> Tuple[int, int, int]:
    x0, x1 = 0, 1
    y0, y1 = 1, 0

    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1

    return a, x0, y0


def find_e(totient):
    e = None
    th = secrets.randbelow(10)
    for i in range(2, totient):
        if math.gcd(totient, i) == 1:
            if th == 0:
                e = i
                break
            else:
                th -= 1
    return e


def to_msg(encoded_msg):
    encoded_msg = str(encoded_msg)[1:]
    decoded_msg = ''
    chunk = 0  # chunk is indexing num
    while len(encoded_msg) > chunk:
        decoded_msg += chr(int(encoded_msg[chunk:chunk+7]))
        chunk += 7
    return decoded_msg


def encrypt(msg, e, n):
    msg = [ord(c) for c in msg]
    encrypted_msg = ["1"]
    chunk = 0  # chunk is split socket
    for i in range(len(msg)):
        if (int(encrypted_msg[chunk]) >= n) or (len(encrypted_msg[chunk]) >= 1000):
            # if over (max encrypt size) or (max socket size):
            encrypted_msg[chunk] = str(pow(int(encrypted_msg[chunk]), e, n))
            chunk += 1
            encrypted_msg.append('1')
        encrypted_msg[chunk] += str(msg[i]).zfill(7)
    encrypted_msg[chunk] = str(pow(int(encrypted_msg[chunk]), e, n))
    return encrypted_msg


def decrypt(encrypted_int, d, n):
    return to_msg(pow(int(encrypted_int), d, n))


def make_prime(seed):
    random.seed(seed)
    return sympy.randprime(100 ** 150, 100 ** 300)


def make_prime_g():
    prime = make_prime(secrets.randbelow(100 ** 200))
    g = secrets.randbelow(prime)
    while g == 0:
        g = secrets.randbelow(prime)

    return prime, g


def setup(prime, g):
    random.seed(secrets.randbelow(100 ** 200))
    a = random.randrange(100 ** 150, 100 ** 300)
    result = pow(g, a, prime)
    return result, prime, a, g
