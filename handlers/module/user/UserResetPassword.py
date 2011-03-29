#!/usr/bin/python
# -*- coding: utf-8 -*-

##
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

import model
from handlers.BaseHandler import *

class UserResetPassword(BaseHandler):

	def execute(self):
		method = self.request.method

		if method == 'GET':
			nickname = self.request.get('nickname')
			token = self.request.get('token')
			u = model.UserData.all().filter('nickname =', nickname).filter('token =', token).get()
			if not u:
				self.render('templates/module/user/user-resetpassword-error.html')
			else:
				self.values['token'] = token
				self.values['nickname'] = nickname
				self.render('templates/module/user/user-resetpassword.html')
		else:
			token = self.request.get('token')
			nickname = self.request.get('nickname')
			password = self.request.get('password')
			re_password = self.request.get('re_password')
		
			if not password or len(password) < 4:
				self.show_error(nickname, token, "Password must contain 4 chars at least")
				return

			if password != re_password:
				self.show_error(nickname, token, "New password and validation password are not equal")
				return
			
			u = model.UserData.all().filter('nickname =', nickname).filter('token =', token).get()
			if not u:
				self.render('templates/module/user/user-resetpassword-error.html')
				return
			
			u.token = None
			u.password = self.hash_password(nickname, password)
			u.put()
			self.render('templates/module/user/user-resetpassword-login.html')

	def show_error(self, nickname, token, error):
		self.values['nickname'] = nickname
		self.values['token'] = token
		self.values['error'] = error
		self.render('templates/module/user/user-resetpassword.html')