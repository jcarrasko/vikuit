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

class CommunityForumMove(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		if user.rol != 'admin':
			self.forbidden()
			return
			
		if method == 'GET':
			thread_key = self.get_param('thread_key')
			
			thread = model.Thread.get(thread_key)
			if thread is None:
				self.not_found()
				return
			
			self.values['thread_key'] = thread.key
			self.render('templates/module/community/community-forum-move.html')
			return
		elif self.auth():
			thread_key = self.get_param('thread_key')
			community_key = self.get_param('community_key')
			thread = model.Thread.get(thread_key)
			community = model.Community.get(community_key)
			
			if community is None or thread is None:
				self.values['thread_key'] = thread.key
				self.values['message'] = "Community not exists."
				self.render('templates/module/community/community-forum-move.html')
				return
			
			if community.title == thread.community.title:
				self.values['thread_key'] = thread.key
				self.values['message'] = "Source and target community are the same one."
				self.render('templates/module/community/community-forum-move.html')
				return
			#decrement threads in previous community
			community_orig = thread.community
			community_orig.threads -= 1
			community_orig.responses= thread.responses
			value = 5 + (2 * thread.responses)
			if community_orig.activity:
				community_orig.activity -= value
			
			#update comments
			responses = model.Thread.all().filter('parent_thread', thread)
			for response in responses:
				response.community = community
				response.community_title = community.title
				response.community_url_path = community.url_path
				response.put()
			
			#change gorup in thread and desnormalizated fields
			thread.community = community
			thread.community_title = community.title
			thread.community_url_path = community.url_path
			
			#increment threads in actual community
			community.threads += 1
			community.responses += thread.responses
			if community.activity:
				community.activity += value
			
			#save fields
			community_orig.put()
			thread.put()
			community.put()
			
			
			self.redirect('/module/community.forum/%s' % (thread.url_path))
			return
			
