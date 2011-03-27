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

import logging
import datetime

from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class CommunityForumEdit(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		if method == "GET" or not self.auth():
			return
		user = self.values['user']
		key = self.get_param('key')
		community = model.Community.get(key)
		if not community:
			self.not_found()
			return
		
		if community.all_users is not None and not self.can_write(community):
			self.forbidden()
			return
		title = self.get_param('title')
		url_path = ''
		content = self.get_param('content')
		preview = self.get_param('preview')
		if preview:
			thread = model.Thread(community=community,
				community_url_path=community.url_path,
				author=user,
				author_nickname = user.nickname,
				title=title,
				content=content,
				responses=0)
			self.values['thread'] = thread
			self.values['preview'] = True
			self.values['is_parent_thread'] = True
			self.render('templates/module/community/community-thread-edit.html')
			return
		
		if self.check_duplicate(community, user, content, title):
			self.show_error("Duplicated thread")
			return
		thread = model.Thread(community=community,
			community_title=community.title,
			community_url_path=community.url_path,
			author=user,
			author_nickname=user.nickname,
			title=title,
			url_path=url_path,
			content=content,
			last_response_date = datetime.datetime.now(),
			responses=0,
			editions=0,
			views=0)
		
		user.threads += 1
		user.put()
		
		self.create_community_subscribers(community)
		
		app = model.Application.all().get()
		if app:
			if not app.threads:
				app.threads = 0
			app.threads += 1
			app.put()
		memcache.delete('app')
		
		thread.put()
		self.add_follower(thread=thread, nickname=user.nickname)
		thread.url_path = ('%d/%s/%s') % (thread.key().id(), self.to_url_path(community.title), self.to_url_path(title))
		subscribe = self.get_param('subscribe')
		if subscribe:
			thread.subscribers.append(user.email)
			self.add_user_subscription(user, 'thread', thread.key().id())
		thread.put()
		memcache.add(str(thread.key().id()) + '_thread', thread, 0)
		community.threads += 1
		if community.activity:
			community.activity += 5
		community.put()
		
		followers = list(self.get_followers(community=community))
		followers.extend(self.get_followers(user=user))
		if not user.nickname in followers:
			followers.append(user.nickname)
		followers = list(set(followers))
		self.create_event(event_type='thread.new', followers=followers, user=user, thread=thread, community=community)
		
		subscribers = community.subscribers
		if subscribers and user.email in subscribers:
			subscribers.remove(user.email)

		if subscribers:
			app = self.get_application()
			subject = self.getLocale("New subject: '%s'") % self.clean_ascii(thread.title)

			body =  self.getLocale("New subject by community %s.\nSubject title: %s\nFollow forum at:\n%s/module/community.forum/%s") % (self.clean_ascii(community.title), self.clean_ascii(thread.title), app.url, thread.url_path)
			self.mail(subject=subject, body=body, bcc=community.subscribers)
		
			
		
		memcache.delete('index_threads')

		self.redirect('/module/community.forum/%s' % thread.url_path)

	def check_duplicate(self, community, user, content, title):
		last_thread = model.Thread.all().filter('community', community).filter('parent_thread', None).filter('author', user).order('-creation_date').get()
		if last_thread is not None:
			if last_thread.title == title and last_thread.content == content:
				return True
		return False
		