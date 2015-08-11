#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Inspired by this code: https://github.com/wwwtyro/webrift/blob/master/server.py

import json
import math
import time

import tornado.websocket
import tornado.web
import tornado.ioloop
import tornado.httpserver

import SensorsInterface

VECT_X = 0.00
VECT_Y = 0.00
VECT_Z = 0.00

SensorsInterface.setupSensorian() #Initialize Sensorian

clients = []

class RotationDataSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		print "Websocket has been opened"
		clients.append(self)
	
	def on_message(self,message):
		print "I have received a message"
	
	def on_close(self):
		print "Websocket closed"
	
	def update(self):
		global VECT_X
		global VECT_Y
		global VECT_Z
		cube_orientation = list(SensorsInterface.getMagnetometer())
		#Low-pass when collecting data from the magnetometer
		VECT_X = 0.2*VECT_X + 0.8*cube_orientation[0]
		VECT_Y = 0.2*VECT_Y + 0.8*cube_orientation[1]
		VECT_Z = 0.2*VECT_Z + 0.8*cube_orientation[2]
		self.write_message(json.dumps((int(VECT_X/100),int(VECT_Y/100),int(VECT_Z/100))))
	

def update():
	for client in clients:
		client.update()

#Create web application
application = tornado.web.Application([(r'/websocket', RotationDataSocket),(r'/web/(.*)',tornado.web.StaticFileHandler, {'path': r'./web/'})])
http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(1982)
callback = tornado.ioloop.PeriodicCallback(update, 1000/120.0) #Poll magnetometer periodically
callback.start()
tornado.ioloop.IOLoop.instance().start()
