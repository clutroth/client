#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal, sys, ssl, logging, os
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
import sqlite3
import string
import hashlib, binascii

logging.basicConfig(format='%(asctime)s %(message)s',


class SimpleEcho(WebSocket):

	def handleMessage(self):
		if self.data is None:
			self.data = ''
		
		try:
			self.sendMessage(str(self.data))
		except Exception as n:
			print n
			
	def handleConnected(self):
		print self.address, 'connected'

	def handleClose(self):
		print self.address, 'closed'


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
                client.sendMessage(str(self.address[0]) + ' - ' + str(self.data))


	def handleConnected(self):
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


if __name__ == "__main__":

	parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
	parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
	parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
	parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
	parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
	parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
	parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
	
	(options, args) = parser.parse_args()

	cls = SimpleEcho
	if options.example == 'chat':
		cls = SimpleChat	

	if options.ssl == 1:
		server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
	else:	
		server = SimpleWebSocketServer(options.host, options.port, cls)

	def close_sig_handler(signal, frame):
		server.close()
		sys.exit()

	signal.signal(signal.SIGINT, close_sig_handler)

	server.serveforever()

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
