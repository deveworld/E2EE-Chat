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


def to_int_list(msg):
    encoded_list = [ord(c) for c in msg]
    return encoded_list


def encrypt(msg, e, n):
    msg = to_int_list(msg)
    encrypted_msg = []
    for i in range(len(msg)):
        encrypted_msg.append(str(pow(msg[i], e, n)))
    return encrypted_msg


def decrypt(encrypted_int, d, n):
    return chr(pow(int(encrypted_int), d, n))


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
