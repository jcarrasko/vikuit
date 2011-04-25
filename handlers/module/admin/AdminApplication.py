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

class AdminApplication(AuthenticatedHandler):

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
			self.values['appName'] 				= self.not_none(app.name)
			self.values['appSubject'] 			= self.not_none(app.subject)
			self.values['locale'] 				= self.not_none(app.locale)
			self.values['url'] 					= self.not_none(app.url)
			self.render('templates/module/admin/admin-application.html')
		elif self.auth():
			app = self.get_application()
			if not app:
				app = model.Application()
				app.users	= model.UserData.all().count()
				app.communities	= model.Community.all().count()
				app.threads = model.Thread.all().filter('parent_thread', None).count()
				app.articles	= model.Article.all().filter('draft =', False).filter('deletion_date', None).count()
			app.name 					= self.get_param('appName')
			app.subject					= self.get_param("appSubject")
			app.locale					= self.get_param("locale")
			app.url						= self.get_param('url')
			app.put()
			memcache.delete('app')
			AppProperties().updateJinjaEnv()
			self.redirect('/module/admin.application?m='+self.getLocale('Updated'))