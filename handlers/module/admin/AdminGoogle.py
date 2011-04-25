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

class AdminGoogle(AuthenticatedHandler):

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
			self.values['recaptcha_public_key'] = self.not_none(app.recaptcha_public_key)
			self.values['recaptcha_private_key']= self.not_none(app.recaptcha_private_key)
			self.values['google_adsense'] 		= self.not_none(app.google_adsense)
			self.values['google_adsense_channel']= self.not_none(app.google_adsense_channel)
			self.values['google_analytics'] 		= self.not_none(app.google_analytics)	
			self.render('templates/module/admin/admin-google.html')
		elif self.auth():
			app = self.get_application()
			if not app:
				app = model.Application()
						
			app.recaptcha_public_key	= self.get_param('recaptcha_public_key')
			app.recaptcha_private_key	= self.get_param('recaptcha_private_key')
			app.google_adsense			= self.get_param('google_adsense')
			app.google_adsense_channel	= self.get_param('google_adsense_channel')
			app.google_analytics		= self.get_param('google_analytics')
			
			app.put()
			memcache.delete('app')
			AppProperties().updateJinjaEnv()
			self.redirect('/module/admin.google?m='+self.getLocale('Updated'))