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
from handlers.module.admin.AdminApplication import *
from handlers.AuthenticatedHandler import *

from utilities.AppProperties import AppProperties

class AdminLookAndFeel(AuthenticatedHandler):

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
			self.values['theme'] 				= self.not_none(app.theme)
			self.values['max_results'] 			= self.not_none(app.max_results)
			self.values['max_results_sublist'] 	= self.not_none(app.max_results_sublist)
			self.render('templates/module/admin/admin-lookandfeel.html')
		elif self.auth():
			app = self.get_application()
			if not app:
				app = model.Application()

			logo = self.request.get("logo")
			if logo:
				app.logo = images.im_feeling_lucky(logo, images.JPEG)
				memcache.delete('/images/application/logo')

			app.theme					= self.get_param("theme") 
			if self.get_param('max_results'):
				app.max_results	= int(self.get_param('max_results'))
			if self.get_param('max_results_sublist'):
				app.max_results_sublist	= int(self.get_param('max_results_sublist'))
			app.put()
			memcache.delete('app')
			AppProperties().updateJinjaEnv()
			self.redirect('/module/admin.lookandfeel?m='+self.getLocale('Updated'))