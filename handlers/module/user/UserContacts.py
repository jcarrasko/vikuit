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

from handlers.BaseHandler import *
from google.appengine.api import users

class UserContacts(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/user.list'
		nickname = self.request.path.split('/')[3]
		this_user = model.UserData.gql('WHERE nickname=:1', nickname).get()
		if not this_user:
			self.not_found()
			return
		# TODO: not show if the user profile is not public
		self.values['this_user'] = this_user
		query = model.Contact.all().filter('user_from', this_user)
		contacts = self.paging(query, 27, '-creation_date', this_user.contacts, ['-creation_date'])
		self.values['users'] = contacts
		self.render('templates/module/user/user-contacts.html')
