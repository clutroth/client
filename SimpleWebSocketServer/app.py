#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import binascii
import hashlib
import math
import os
import sys
import random
import signal
import ssl
import string
import sqlite3
import time
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket


class DataBase(object):
    def __init__(self, fileName='baza.db'):
        self.fileName = fileName
        self.USER_TABLE_NAME = 'user'

    def addUser(self, name, salt, password):
        self.exe(
            'INSERT INTO {0} VALUES (NULL, \'{1}\', \'{2}\', \'{3}\');'.format(
                self.USER_TABLE_NAME, name, salt, password
            )
        )

    def exe(self, s):
        self.con = sqlite3.connect(self.fileName)
        c = self.con.cursor()
        c.execute(s)
        ret = c.fetchall()
        self.con.commit()
        self.con.close()
        return ret


class User(object):
    MIN_ENTROPHY = 44
    HASH_NAME = 'sha256'
    SALT_SIZE = 32
    ROUNDS = 100
    ALLOWED_NAME_CHARTERS = string.lowercase + string.digits + '_'

    def __init__(self, name, plainTextPassword, confirm):
        if len(set(name) - set(self.ALLOWED_NAME_CHARTERS)) is not 0:
            raise AttributeError(Parser.NAME_CHAR_ERR)
        if confirm != plainTextPassword:
            raise AttributeError(Parser.PWDS_NOT_MATCH)
        if self.entophy(plainTextPassword) < self.MIN_ENTROPHY:
            raise AttributeError(Parser.PWD_TOO_WEEK)
        self.name = name
        self.salt = binascii.hexlify(os.urandom(self.SALT_SIZE))
        self.password = self.hashPassword(plainTextPassword,
                                          self.salt)
        self.loggedIn = False

    def hashPassword(self, plainTextPassword, salt, hashName=HASH_NAME, rounds=ROUNDS):
        h = hashlib.new(hashName)
        for x in xrange(rounds):
            h.update(plainTextPassword + salt)
        return h.hexdigest()

    def entophy2(self, text):
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
            e += p * math.log(p, 2)
        return -e

    def entophy(self, text):
        length = 0
        littleAlphabets = [
            string.uppercase,
            string.lowercase,
            string.digits,
            string.punctuation]
        for a in littleAlphabets:
            if set(text).isdisjoint(set(a)) is False:
                length += len(a)
        return len(text) * math.log(length, 2)


class Parser(object):
    ADD_USER = 'adduser'
    LOGIN_NAME_EXISTS = 'login name exists'
    NO_COMMAND = 'command is excepted'
    ADDED_SUCCESFULL = 'user added succesfull'
    PWDS_NOT_MATCH = 'passwords does not match'
    PWD_TOO_WEEK = 'password is too week'
    NAME_CHAR_ERR = 'name contains invalid charters'

    def __init__(self, client):
        self.ws = client
        self.db = DataBase()

    def parse(self, cmd):
        cmd = self.prepare(cmd)
        if len(cmd) is 0:
            self.ws.sendMessage(self.NO_COMMAND)
            raise Exception('no msg')
        if cmd[0] == self.ADD_USER and len(cmd) == 4:
            # useradd username password confirm
            userName = cmd[1]
            userPassword = cmd[2]
            confirmPassword = cmd[3]
            try:
                new = User(userName, userPassword, confirmPassword)
            except AttributeError as e:
                self.ws.sendMessage(e.message)
                return
            try:
                self.db.addUser(new.name, new.salt, new.password)
            except sqlite3.IntegrityError:
                self.ws.sendMessage(self.LOGIN_NAME_EXISTS)
                return
            self.ws.sendMessage(self.ADDED_SUCCESFULL)

    def prepare(self, cmd):
        cmd = cmd.replace('"', '""')
        cmd = cmd.split()
        return cmd


class TooFewArguments(ValueError):
    pass


class SimpleChat(WebSocket):

    def handleMessage(self):
        time.sleep(random.random())
        if self.data is None:
            self.data = ''

        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0])
                                       + ' - ' + str(self.data))
                except Exception as n:
                    print(n)
            else:
                arg = str(self.data)
                self.f.parse(arg)

    def handleConnected(self):
        time.sleep(random.random())
        print(self.address, 'connected')
        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0]) + ' - connected')
                except Exception as n:
                    print(n)
            else:
                self.f = Parser(client)

    def handleClose(self):
        print(self.address, 'closed')
        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0]) + ' - disconnected')
                except Exception as n:
                    print(n)

if __name__ == "__main__":
    HOSTNAME = ''
    PORT = 8000
    CLS = SimpleChat
    CERT_FILE = 'cert.pem'
    KEY_FILE = CERT_FILE
    server = SimpleSSLWebSocketServer(
        HOSTNAME, PORT, CLS, CERT_FILE, KEY_FILE, ssl.PROTOCOL_TLSv1
    )

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    server.serveforever()
