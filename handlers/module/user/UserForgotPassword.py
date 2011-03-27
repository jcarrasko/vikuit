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
import random

from handlers.BaseHandler import *
from google.appengine.api import mail
from utilities.AppProperties import AppProperties

class UserForgotPassword(BaseHandler):

	def execute(self):
		method = self.request.method
		
		if method == 'GET':
			self.values['redirect_to'] = self.request.get('redirect_to')
			self.render('templates/module/user/user-forgotpassword.html')
		else:
			email = self.request.get('email')
			u = model.UserData.all().filter('email =', email).get()
			if not u:
				self.show_error(email, "No user found with this mail")
				return
			
			# only local accounts can reset password
			app = self.get_application()
			subject = self.getLocale("Password recovery")#u"Recuperar password"
			if u.registrationType is None or u.registrationType == 0:
				u.token = self.hash(str(random.random()), email)
				u.put()
				#Haz click en el siguiente enlace para proceder a establecer tu password.\n%s/module/user.resetpassword?nickname=%s&token=%s
				body = self.getLocale("Click this link to set your password.\n%s/module/user.resetpassword?nickname=%s&token=%s") % (app.url, u.nickname, u.token)
			else:
				accountProvider = AppProperties().getAccountProvider(u.registrationType)
				body = self.getLocale("You have requested to recover password but credentials you use in %s are from %s. Review your login information.") % (app.name, accountProvider)
				
			self.mail(subject=subject, body=body, to=[u.email])
			
			self.values['token'] = u.token
			self.values['email'] = email
			self.values['redirect_to'] = self.request.get('redirect_to')
			self.render('templates/module/user/user-forgotpassword-sent.html')

	def show_error(self, email, error):
		self.values['email'] = email
		self.values['error'] = error
		self.render('templates/module/user/user-forgotpassword.html')