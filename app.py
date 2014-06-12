#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ssl
import os, sys
import sqlite3
import string
import hashlib, binascii
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
import signal

class DataBase:
    def __init__(self, fileName='baza.db'):
        self.fileName = fileName
        self.USER_TABLE_NAME = 'user'
    def connect(self):
        self.con = sqlite3.connect(self.fileName)
    def close(self):
        self.con.commit()
        self.con.close()
    def cursor(self):
        return self.con.cursor()
    def addUser(self, name, salt, password):
        self.connect()
        c = self.cursor()
        c.execute('INSERT INTO {0} VALUES (NULL, \'{1}\', \'{2}\', \'{3}\');'.format(self.USER_TABLE_NAME, name, salt, password))
        self.close()
class User:
    def __init__(self, name, plainTextPassword):
        HASH_NAME = 'sha256'
        SALT_SIZE = 32
        ROUNDS = 100
        ALLOWED_NAME_CHARTERS = string.lowercase + string.digits + '_'
        if len(set(name) - set(ALLOWED_NAME_CHARTERS)) is not 0:
            print set(ALLOWED_NAME_CHARTERS)
            print set(name)
            print set(name) - set(ALLOWED_NAME_CHARTERS)
            raise ValueError('name contains invalid charters')
        self.name = name
        self.salt = binascii.hexlify(os.urandom(SALT_SIZE))
        self.password = self.hashPassword(HASH_NAME, plainTextPassword, self.salt, ROUNDS)
    def hashPassword(self, hashName, plainTextPassword, salt, rounds):
        h = hashlib.new(hashName)
        for x in xrange(rounds):
            h.update(plainTextPassword + salt)
        return h.hexdigest()




class Universe:
    def __init__(self):
        self.db = DataBase()
    def newUser(self, name, plainTextPassword):
        new = User(name, plainTextPassword)
        self.db.addUser(new.name, new.salt, new.password)

class TooFewArguments(ValueError):
    pass

class SimpleChat(WebSocket):

    def handleMessage(self):
        if self.data is None:
            self.data = ''

        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0]) + ' - ' + str(self.data))
                except Exception as n:
                    print n
            else:
                client.sendMessage(str(self.address[0]) + ' - ' + str(self.data))
                print 'Wysłano wiad. do', self.address

    def handleConnected(self):
        self.SEP = ' '
        slef.u = Universe()
        print self.address, 'connected'
        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0]) + ' - connected')
                except Exception as n:
                    print n

    def handleClose(self):
        print self.address, 'closed'
        for client in self.server.connections.itervalues():
            if client != self:
                try:
                    client.sendMessage(str(self.address[0]) + ' - disconnected')
                except Exception as n:
                    print n
    def command(self):
        order = self.data.split(self.SEP)
        if order[0] == 'register':
            if len(order) < 3:
                raise TooFewArguments("register $username $password");
            else :
                self.u.newUser(order[1], order[2])
                print 'Dodano użytkownika {0}' % (order[1])





if __name__ == "__main__":
    HOSTNAME = 'volt.iem.pw.edu.pl'
    PORT = 2812
    CLS = SimpleChat
    CERT_FILE = 'cert.pem'
    KEY_FILE = CERT_FILE
    server = SimpleSSLWebSocketServer(HOSTNAME, PORT, CLS, CERT_FILE, KEY_FILE, ssl.PROTOCOL_SSLv3)
    dir(server)


    print "Ruszyli!i"

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    server.serveforever()


