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

from google.appengine.api import mail
from handlers.AuthenticatedHandler import *

class UserContact(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		user_to = model.UserData.all().filter('nickname', self.get_param('user_to')).get()
		if not user_to:
			self.not_found()
			return
			
		if not self.auth():
			return
		
		contact = model.Contact.all().filter('user_from', user).filter('user_to', user_to).get()
		if not contact:
			contact = model.Contact(user_from=user,
				user_to=user_to,
				user_from_nickname=user.nickname,
				user_to_nickname=user_to.nickname)
			contact.put()
			
			user.contacts += 1
			user.put()
			self.add_follower(user=user_to, nickname=user.nickname)
			
			followers = list(self.get_followers(user=user))
			followers.append(user.nickname)
			if not user_to.nickname in followers:
				followers.append(user_to.nickname)
			self.create_event(event_type='contact.add', followers=followers, user=user, user_to=user_to)
			
			app = self.get_application()
			subject = self.getLocale("%s has added you as contact") % user.nickname # "%s te ha agregado como contacto"
			# %s te ha agregado como contacto en %s\nPuedes visitar su perfil en: %s/module/user/%s\n
			body = self.getLocale("%s has added you as contact in %s\nVisit profile page: %s/module/user/%s\n") % (user.nickname, app.url, app.url, user.nickname)
			self.mail(subject=subject, body=body, to=[user_to.email])
			
			if self.get_param('x'):
				self.render_json({ 'action': 'added' })
			else:
				self.redirect('/module/user/%s' % user_to.nickname)
		else:
			contact.delete()
			user.contacts -= 1
			user.put()
			self.remove_follower(user=user_to, nickname=user.nickname)
			
			if self.get_param('x'):
				self.render_json({ 'action': 'deleted' })
			else:
				self.redirect('/module/user/%s' % user_to.nickname)
