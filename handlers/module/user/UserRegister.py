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

import re
import random
import model

from handlers.BaseHandler import *

from os import environ
from recaptcha import captcha

class UserRegister(BaseHandler):

	def execute(self):
		method = self.request.method
		if method == 'GET':
			self.send_form(None)
		else:
			if self.get_param('x'):
				# check if nickname is available
				nickname = self.request.get('nickname')
				email = self.request.get('email')
				message = self.validate_nickname(nickname)
				if message:
					self.render_json({'valid': False, 'message': message})
				else :
					self.render_json({'valid': True })
				return
			else:
				# Validate captcha
				challenge = self.request.get('recaptcha_challenge_field')
				response  = self.request.get('recaptcha_response_field')
				remoteip  = environ['REMOTE_ADDR']

				cResponse = captcha.submit(
					challenge,
					response,
					self.get_application().recaptcha_private_key,
					remoteip)

				if not cResponse.is_valid:
					# If the reCAPTCHA server can not be reached, 
					# the error code recaptcha-not-reachable will be returned.
					self.send_form(cResponse.error_code)
					return
				
				nickname = self.request.get('nickname')
				email = self.request.get('email')
				password = self.request.get('password')
				re_email = self.request.get('re_email')
				re_password = self.request.get('re_password')

				if not self.get_param('terms-and-conditions'):
					self.show_error(nickname, email, "You must accept terms and conditions" )
					return
			
				if not re.match('^[\w\.-]{3,}@([\w-]{2,}\.)*([\w-]{2,}\.)[\w-]{2,4}$', email):
					self.show_error(nickname, email, "Enter a valid mail" )
					return

				if not re.match('^[\w\.-]+$', nickname):
					self.show_error(nickname, email,  "Username can contain letters, numbers, dots, hyphens and underscores" )
					return

				if not password or len(password) < 4 or len(password) > 30:
					self.show_error(nickname, email,  "Password must contain between 4 and 30 chars" )
					return
				message = self.validate_nickname(nickname)
				if message:
					self.show_error(nickname, email, message)
					return
			
				u = model.UserData.all().filter('email =', email).get()
				if u:
					self.show_error(nickname, email,  "This mail already exists" )
					return
				
				if email != re_email:
					self.show_error(nickname, email,  "Mail and validation mail are not equals" )
					return
				
				if password != re_password:
					self.show_error(nickname, email,  "New password and validation password are not equal" )
					return
			
					times = 5
			
				user = model.UserData(nickname=nickname,
					email=email,
					password=self.hash_password(nickname, password),
					articles=0,
					draft_articles=0,
					messages=0,
					draft_messages=0,
					comments=0,
					rating_count=0,
					rating_total=0,
					rating_average=0,
					threads=0,
					responses=0,
					communities=0,
					favourites=0,
					public=False,
					contacts=0)
				user.registrationType = 0#local identifier
				user.put()
				
				app = model.Application.all().get()
				if app:
					app.users += 1
					app.put()
				memcache.delete('app')

				#send welcome email
				app = self.get_application()
				subject = self.getLocale("Welcome to %s") % app.name
				bt = "Thanks for signing in %s. %s team welcome you to our social network. \n\nComplete your profile \n%s/module/user.edit\n\nPublish articles, \n\n\nBe part of the communities that interest you. Each community has a forum to share or discuss with people to whom the same interests as you.\nCommunities list %s/module/community.list\nThread list %s/forum.list\n\n\n\nFor futher information check our FAQ page\n%s/html/faq.html\n\nBest regards,\n\n%s Team."
				body = self.getLocale(bt) % (app.name, app.name, app.url, app.url, app.url, app.url, app.name)
				self.mail(subject=subject, body=body, to=[user.email])
				self.sess.store(str(user.key()), 7200)
				rt = self.request.get('redirect_to')
				if not rt:
					rt = '/'
				self.redirect(rt)

	def show_error(self, nickname, email, error):
		chtml = self.get_captcha(None)
		self.values['captchahtml'] = chtml
		self.values['nickname'] = nickname
		self.values['email'] = email
		self.values['error'] = error
		self.render('templates/module/user/user-register.html')
	
	def match(self, pattern, value):
		m = re.match(pattern, value)
		if not m or not m.string[m.start():m.end()] == value:
			return None
		return value
		
	def send_form(self, error):
		chtml = self.get_captcha(error)
		self.values['captchahtml'] = chtml
		self.values['redirect_to'] = self.request.get('redirect_to')
		self.render('templates/module/user/user-register.html')
		
	def get_captcha(self, error):
		chtml = captcha.displayhtml(
			public_key = self.get_application().recaptcha_public_key,
			use_ssl = False,
			error = error)
		return chtml

	def validate_nickname(self, nickname):
		if len(nickname) < 4:
			return self.getLocale("Username must contain 4 chars at least")

		if len(nickname) > 20:
			return self.getLocale("Username must contain less than 20 chars")

		u = model.UserData.all().filter('nickname =', nickname).get()
		if u:
			return self.getLocale("User already exists")
			
		return ''