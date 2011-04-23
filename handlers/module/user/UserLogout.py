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
from google.appengine.api import users

class UserLogout(BaseHandler):

	def execute(self):
		#Check if google account is in use
		#User registered with different user in vikuit and google
		user = users.get_current_user()
		userLocalId = self.sess.user
		googleAc = False
		if user and userLocalId:
			userLocal = db.get(userLocalId)
			if userLocal and user.email() == userLocal.email:
				googleAc = True
			
			
		redirect = '/'
		try:
			if self.auth():
				self.sess.store('', 0)
			if self.request.referrer:
				redirect = self.request.referrer
		except KeyError:
			self.redirect(redirect)
			return
			
		if googleAc:
			self.redirect(users.create_logout_url(redirect))
		else: 
			self.redirect(redirect)