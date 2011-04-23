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

import datetime

from handlers.BaseHandler import *
from google.appengine.api import users

class UserList(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/user.list'
		app = self.get_application()
		query = model.UserData.all()
		key = '%s?%s' % (self.request.path, self.request.query)
		results = 10
		if app.max_results:
			results = app.max_results
		users = self.paging(query, results, '-articles', app.users, ['-creation_date', '-articles'], key)
		if users is not None:
			self.values['users'] = users
			self.add_tag_cloud()
		self.render('templates/module/user/user-list.html')
