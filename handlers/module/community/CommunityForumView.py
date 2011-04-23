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

class CommunityForumView(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/community.list'
		user = self.values['user']
		url_path = self.request.path.split('/', 3)[3]
		thread_id = self.request.path.split('/')[3]
		thread = self.cache(thread_id + '_thread', self.get_thread)
		#thread = model.Thread.all().filter('url_path', url_path).filter('parent_thread', None).get()
		if not thread:
			# TODO: try with the id in the url_path and redirect
			self.not_found()
			return
		if thread.deletion_date:
			self.not_found()
			return
		# migration. supposed to be finished
		if len(thread.url_path.split('/')) == 2:
			thread.url_path = '%d/%s' % (thread.key().id(), thread.url_path)
			thread.parent_thread = None
			thread.put()
			self.redirect('/module/community.forum/%s' % thread.url_path)
			return
		# end migration
		'''if thread.views is None:
			thread.views = 0;
		thread.views += 1
		thread.put()'''
		
		community = thread.community

		self.values['community'] = community
		self.values['joined'] = self.joined(community)
		self.values['thread'] = thread
		query = model.Thread.all().filter('parent_thread', thread)
		results = 20
		app = self.get_application()
		if app.max_results_sublist:
			results = app.max_results_sublist
		key = '%s?%s' % (self.request.path, self.request.query)
		responses = self.paging(query, results, 'creation_date', thread.responses, ['creation_date'], key=key, timeout=0)
		#responses = self.cache(url_path, self.get_responses)
		# migration
		if not thread.author_nickname:
			thread.author_nickname = thread.author.nickname
			thread.put()
		i = 1
		for t in responses:
			if not t.response_number:
				t.response_number = i
				t.put()
			i += 1
		# end migration
				
		self.values['responses'] = responses
		
		if community.all_users:
			self.values['can_write'] = True
		else:
			self.values['can_write'] = self.can_write(community)
		if user:
			if user.email in thread.subscribers:
				self.values['cansubscribe'] = False
			else:
				self.values['cansubscribe'] = True

		self.values['a'] = 'comments'
		self.render('templates/module/community/community-forum-view.html')
		
	def get_thread(self):
		url_path = self.request.path.split('/', 3)[3]
		return model.Thread.all().filter('url_path', url_path).filter('parent_thread', None).get()

		
