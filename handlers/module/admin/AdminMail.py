#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Blanco <jose.blanco[a]vikuit.com>
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>
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

import img

from google.appengine.api import images
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

from utilities.AppProperties import AppProperties

class AdminMail(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		self.values['tab'] = '/admin'
		
		if user.rol != 'admin':
			self.forbidden()
			return
		
		if method == 'GET':
			app = self.get_application()
			self.values['m'] = self.get_param('m')
			if not app:
				app = model.Application()
			self.values['app'] = app
			self.values['mail_contact'] 		= self.not_none(app.mail_contact)
			self.values['mail_subject_prefix'] 	= self.not_none(app.mail_subject_prefix)
			self.values['mail_sender'] 			= self.not_none(app.mail_sender)
			self.values['mail_footer'] 			= self.not_none(app.mail_footer)
			self.render('templates/module/admin/admin-mail.html')
		elif self.auth():
			app = self.get_application()
			if not app:
				app = model.Application()
			app.mail_subject_prefix		= self.get_param('mail_subject_prefix')
			app.mail_contact				= self.get_param('mail_contact')
			app.mail_sender				= self.get_param('mail_sender')
			app.mail_footer				= self.get_param('mail_footer')
			app.put()
			memcache.delete('app')
			AppProperties().updateJinjaEnv()
			self.redirect('/module/admin.mail?m='+self.getLocale('Updated'))