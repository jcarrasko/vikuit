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


from google.appengine.ext import db
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class CommunityDelete(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		
		if user.rol != 'admin':
			self.forbidden()
			return
		
		if not self.auth():
			return
		
		community=model.Community.get(self.get_param('key'))
		db.delete(community.communityuser_set)
		db.delete(community.communityarticle_set)
		db.delete(community.thread_set)
		community.delete()
		
		app = app = model.Application.all().get()
		if app:
			app.communities -=1
			app.put()
		memcache.delete('app')
		# TODO: some other memcache value should be removed? most active communities?
		self.redirect('/')
