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

class CommunityMove(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		if user.rol != 'admin':
			self.forbidden()
			return
			
		if method == 'GET':
			action = self.get_param('action')
			key = self.get_param('key_orig')
			if key:
				community_orig = model.Community.get(key)
				self.values['key_orig'] = community_orig.key
			self.render('templates/module/community/community-move.html')
			return
		elif self.auth():
			action = action = self.get_param('action')
			if not action:
				self.render('templates/module/community/community-move.html')
				return
			key_orig = self.get_param('key_orig')
			if key_orig:
				community_orig = model.Community.get(key_orig)
			key_dest = self.get_param('key_dest')
			if key_dest:
				community_dest = model.Community.get(key_dest)
			mesagge = ''
			if not community_orig:
				message = self.getLocale("Source community not exists") 
				self.values['message'] = message
				self.render('templates/module/community/community-move.html')
				return
			elif not community_dest:
				message = self.getLocale("Taget community not exists") 
				self.values['message'] = message
				self.render('templates/module/community/community-move.html')
				return
			elif action == 'mu':
				#move users
				message = self.move_users(community_orig, community_dest)
			elif action == 'mt':
				#move threads
				message = self.move_threads(community_orig, community_dest)
				memcache.delete('index_threads')
			elif action == 'mi':
				#move articles
				message = self.move_articles(community_orig, community_dest)
			elif action == 'delete':
				message = self.delete_community(community_orig)
				memcache.delete('index_communities')
			if action != 'delete':
				self.values['key_orig'] = community_orig.key
				self.values['key_dest'] = community_dest.key
			self.values['message'] = message
			self.render('templates/module/community/community-move.html')
			return 
	
	def move_articles(self, community_orig, community_dest):
		community_articles = model.CommunityArticle.all().filter('community', community_orig).fetch(10)
		counter = 0
		for community_article in community_articles:
			article_dest = model.CommunityArticle.all().filter('community', community_dest).filter('article', community_article.article).get()
			if article_dest:
				community_article.delete()
			else:
				community_article.community = community_dest
				community_article.community_title = community_dest.title
				community_article.community_url_path = community_dest.url_path
				community_article.put()
				community_dest.articles += 1
				if community_dest.activity:
					community_dest.activity += 15
				community_dest.put()
				counter +=1
			community_orig.articles -= 1
			if community_dest.activity:
				community_dest.activity -= 15
			community_orig.put()
		
		return self.getLocale("%s articles moved. Source community contains %s more.") % (counter, community_orig.articles)
		
	def move_threads(self, community_orig, community_dest):
		counter = 0
		for community_thread in model.Thread.all().filter('community', community_orig).filter('parent_thread', None).fetch(1):
		
			community_thread.community = community_dest
			community_thread.community_url_path = community_dest.url_path
			community_thread.community_title = community_dest.title
			responses = model.Thread.all().filter('parent_thread', community_thread)
			if responses:
				for response in responses:
					response.community = community_dest
					response.community_url_path = community_dest.url_path
					response.community_title = community_dest.title
					response.put()
					counter +=1
		
			community_thread.put()
			community_orig.threads -= 1
			community_orig.comments -= community_thread.comments
			value = 5 + (2 * thread.responses)
			if community_orig.activity:
				community_dest.activity -= value
			community_orig.put()
			community_dest.threads += 1
			community_dest.comments += community_thread.comments
			if community_dest.activity:
				community_dest.activity += value
				community_dest.put()
		return self.getLocale("Moved thread with %s replies. %s threads remain.") % (counter, community_orig.threads)
		
		
	def move_users(self, community_orig, community_dest):
		community_users = model.CommunityUser.all().filter('community', community_orig).fetch(10)
		counter = 0
		for community_user in community_users:
			user_dest = model.CommunityUser.all().filter('community', community_dest).filter('user', community_user.user).get()
			if user_dest:
				community_user.user.communities -= 1
				community_user.user.put()
				self.remove_user_subscription(community_user.user, 'community', community_orig.key().id())
				community_user.delete()
			else:
				community_user.community = community_dest
				community_dest.members += 1
				community_dest.subscribers.append(community_user.user.email)
				self.add_follower(community=community_dest, nickname=community_user.user.nickname)
				self.add_user_subscription(community_user.user, 'community', community_dest.key().id())
				if community_dest.activity:
					community_dest.activity += 1
				community_dest.put()
				counter += 1
				community_user.community_title = community_dest.title
				community_user.community_url = community_dest.url_path
				community_user.put()
			
			community_orig.members -= 1
			if community_orig.activity:
				community_orig.activity -= 1
			community_orig.put()

		return self.getLocale("Moved %s users. Source community contains %s more.") % (counter, community_orig.members)
	
	def delete_community(self, community_orig):
		community_orig.delete()
		app = model.Application.all().get()
		if app:
			app.communities -= 1
			app.put()
			memcache.delete('app')
		return self.getLocale("Deleted community. %s communities remain.") % (app.communities)
