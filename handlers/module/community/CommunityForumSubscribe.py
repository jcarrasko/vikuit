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
from handlers.AuthenticatedHandler import *


class CommunityForumSubscribe( AuthenticatedHandler ):

	def execute(self):
		key = self.get_param('key')#TODO if key is empty app crashed
		thread = model.Thread.get(key)
		memcache.delete(str(thread.key().id()) + '_thread')
		user = self.values['user']
		mail = user.email
		
		if not mail in thread.subscribers:
			if not self.auth():
				return
			thread.subscribers.append(user.email)
			thread.put()
			self.add_user_subscription(user, 'thread', thread.key().id())
			memcache.add(str(thread.key().id()) + '_thread', thread, 0)
			if self.get_param('x'):
				self.render_json({ 'action': 'subscribed' })
			else:	
				self.redirect('/module/community.forum/%s' % thread.url_path)
		else:
			auth = self.get_param('auth')
			if not auth:
				self.values['thread'] = thread
				self.render('templates/module/community/community-forum-subscribe.html')
			else:
				if not self.auth():
					return
				thread.subscribers.remove(user.email)
				thread.put()
				self.remove_user_subscription(user, 'thread', thread.key().id())
				if self.get_param('x'):
					self.render_json({ 'action': 'unsubscribed' })
				else:	
					self.redirect('/module/community.forum/%s' % thread.url_path)

