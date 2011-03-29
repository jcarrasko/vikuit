#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>
# (C) Copyright 2011 Jose Blanco <jose.blanco[a]vikuit.com>
# 
# This file is part of "vikuit".
# 
# "vikuit" is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# "vikuit" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with "vikuit".  If not, see <http://www.gnu.org/licenses/>.
##
import os
import sha
import time
import Cookie

COOKIE_NAME = 'vikuit'

class Session(object):

	def __init__(self, seed):
		self.time  = None
		self.user  = None
		self.auth  = None
		self.seed  = seed
	
	def load(self):
		string_cookie = os.environ.get('HTTP_COOKIE', '')
		string_cookie = string_cookie.replace(';', ':') # for old sessions
		self.cookie = Cookie.SimpleCookie()
		self.cookie.load(string_cookie)
		if self.cookie.get(COOKIE_NAME):
			value  = self.cookie[COOKIE_NAME].value
			tokens = value.split(':')
			if len(tokens) != 3:
				return False
			else:
				h = tokens[2]
				tokens = tokens[:-1]
				tokens.append(self.seed)
				if h == self.hash(tokens):
					self.time = tokens[0]
					self.user = tokens[1]
					self.auth = h
					try:
						t = int(self.time)
					except:
						return False
					if t > int(time.time()):
						return True
		return False
	
	def store(self, user, expire):
		self.time = str(int(time.time())+expire)
		self.user = user
		params = [self.time, self.user, self.seed]
		self.auth = self.hash(params)
		params = [self.time, self.user, self.auth]
		self.cookie[COOKIE_NAME] = ':'.join(params)
		self.cookie[COOKIE_NAME]['expires'] = expire
		self.cookie[COOKIE_NAME]['path'] = '/'
		print 'Set-Cookie: %s; HttpOnly' % (self.cookie.output().split(':', 1)[1].strip())
	
	def hash(self, params):
		return sha.new(';'.join(params)).hexdigest()
	
	"""
	def __str__(self):	
		params = [self.time, self.user, self.auth]
		self.cookie[COOKIE_NAME] = ':'.join(params)
		self.cookie[COOKIE_NAME]['path'] = '/'
		return self.cookie.output()

s = Session('1234')
s.load()
if s.load():
	print s.auth
	print s.user
s.store('anabel', 3200)

	"""