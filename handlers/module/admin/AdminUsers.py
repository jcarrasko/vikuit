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


from handlers.AuthenticatedHandler import *

class AdminUsers(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		self.values['tab'] = '/admin'
		
		if user.rol != 'admin':
			self.forbidden()
			return
		
		if method == 'GET':
			self.render('templates/module/admin/admin-users.html')
		elif self.auth():
			nickname = self.get_param('nickname')
			if nickname is None or nickname == '':
				self.values['m'] = "Complete Nickname field"
				self.render('/admin-users.html')
				return
			u = model.UserData.all().filter('nickname', nickname).get()
			if u is None:
				self.values['m'] = "User '%s' doesn't exists"
				self.values['arg'] = nickname
				self.render('/admin-users.html')
				return
			action = self.get_param('action')
			if action == 'block_user':
				u.banned_date = datetime.datetime.now()
				u.put()
				self.values['m'] = "User '%s' was blocked"
				self.values['arg'] = nickname
			elif action == 'unblock_user':
				u.banned_date = None
				u.put()
				self.values['m'] = "User '%s' was unlocked"
				self.values['arg'] = nickname
			else:
				self.values['m'] = "Action '%s' not found"
				self.values['arg'] = action
			self.render('/admin-users.html')