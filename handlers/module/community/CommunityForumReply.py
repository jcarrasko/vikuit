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

from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class CommunityForumReply(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		if method == "GET" or not self.auth():
			return
		
		user = self.values['user']
		key = self.get_param('key')
		thread = model.Thread.get(key)
		memcache.delete(str(thread.key().id()) + '_thread')
		if not thread:
			self.not_found()
			return
		community = thread.community
		if community.all_users is not None and not self.can_write(community):
			self.forbidden()
			return
		content = self.get_param('content')
		preview = self.get_param('preview')
		
		if preview:
			response = model.Thread(community=community,
				author=user,
				author_nickname=user.nickname,
				title=thread.title,
				content=content,
				parent_thread=thread,
				responses=0)
			self.values['thread'] = response
			self.values['preview'] = True
			self.render('templates/module/community/community-thread-edit.html')
			return
		if self.check_duplicate(community, user, thread, content):
			self.show_error("Duplicated reply")
			return
		response = model.Thread(community=community,
			community_title=community.title,
			community_url_path=community.url_path,
			author=user,
			author_nickname=user.nickname,
			title=thread.title,
			url_path=thread.url_path,
			content=content,
			parent_thread=thread,
			response_number=thread.responses+1,
			responses=0,
			editions=0)
		response.put()
		results = 20
		app = self.get_application()
		if app.max_results_sublist:
			results = app.max_results_sublist
		page = response.response_number / results
		if (response.response_number % results) == 1:
			#delete previous page from the cache
			if page != 1:
				previous_url = '/module/community.forum/%s?p=%d' % (thread.url_path, page)
			else:
				previous_url = '/module/community.forum/%s?' % (thread.url_path)
			memcache.delete(previous_url)
			
		if (response.response_number % results) > 0:
			page += 1
		if page != 1:
			response_url = '/module/community.forum/%s?p=%d' % (thread.url_path, page)
		else:
			response_url = '/module/community.forum/%s?' % (thread.url_path)
		memcache.delete(response_url)
		response_url = response_url + '#comment-%d' % (response.response_number)
		self.create_community_subscribers(community)
		community.responses = community.responses + 1
		community.put()
		
		followers = list(self.get_followers(user=user))
		followers.append(user.nickname)
		followers.extend(self.get_followers(thread=thread))
		followers = list(set(followers))
		self.create_event(event_type='thread.reply', followers=followers,
			user=user, thread=thread, community=community, response_number=response.response_number)
		
		subscribers = thread.subscribers
		email_removed = False
		if subscribers and user.email in subscribers:
			email_removed = True
			subscribers.remove(user.email)

		if subscribers:
			subject = self.getLocale("New reply to: '%s'") % self.clean_ascii(thread.title) # "Nueva respuesta en: '%s'"

			body = self.getLocale("New reply to %s.\n%s%s\n\nAll replies:\n%s/module/community.forum/%s\n\nRemove this subscription:\n%s/module/community.forum.subscribe?key=%s") % (self.clean_ascii(thread.title), app.url, response_url, app.url, thread.url_path, app.url, str(thread.key()))
			self.mail(subject=subject, body=body, bcc=thread.subscribers)
		
		subscribe = self.get_param('subscribe')
		if email_removed:
			thread.subscribers.append(user.email)
		if subscribe and not user.email in thread.subscribers:
			thread.subscribers.append(user.email)
			self.add_user_subscription(user, 'thread', thread.key().id())
		thread.responses += 1
		thread.last_response_date = datetime.datetime.now()
		thread.put()
		memcache.add(str(thread.key().id()) + '_thread', thread, 0)
		
		community = thread.community
		if community.activity:
			community.activity += 2
		community.put()
		memcache.delete('index_threads')

		self.redirect(response_url)
		
	def check_duplicate(self, community, user, parent_thread, content):
		last_thread = model.Thread.all().filter('community', community).filter('parent_thread', parent_thread).filter('author', user).order('-creation_date').get()
		if last_thread is not None:
			if last_thread.content == content:
				return True
		return False
