#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from math import log


def entrophy(text):
    alphabet = [0] * 256
    for c in text:
        alphabet[ord(c)] += 1
    while True:
        try:
            alphabet.remove(0)
        except:
            break
    e = 0
    for a in alphabet:
        p = float(a) / len(text)
        e += p * log(p, 2)
    return -e

s = 'symbols2;'
print(entrophy(s))
s = 'gwjefoh98q0fe,kl-sap0-iewq0liwqf00q9i321ure9i0qd[fd3219;re3;098e'
print(entrophy(s))
