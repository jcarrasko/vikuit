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

import img

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class CommunityEdit(AuthenticatedHandler):

	def execute(self):
		self.values['tab'] = '/module/community.list'
		method = self.request.method
		user = self.values['user']
		key = self.get_param('key')

		if method == 'GET':
			if key:
				# show edit form
				community = model.Community.get(key)
				if user.nickname != community.owner.nickname and user.rol != 'admin':
					self.forbidden()
					return
				self.values['key'] = key

				self.values['title'] = community.title
				self.values['description'] = community.description
				if community.all_users is not None:
					self.values['all_users'] = community.all_users
				else:
					self.values['all_users'] = True
				if community.category:
					self.values['category'] = community.category
				self.add_categories()
				self.render('templates/module/community/community-edit.html')
			else:
				# show an empty form
				self.values['title'] = "New community..."
				self.values['all_users'] = True
				self.add_categories()
				self.render('templates/module/community/community-edit.html')
		elif self.auth():
			if key:
				# update community
				community = model.Community.get(key)
				if user.nickname != community.owner.nickname and user.rol != 'admin':
					self.forbidden()
					return
				# community title is not editable since many-to-many relationships are denormalizated
				# community.title = self.get_param('title')
				community.description = self.get_param('description')
				image = self.request.get("img")
				if image:
					image = images.im_feeling_lucky(image, images.JPEG)
					community.avatar = img.resize(image, 128, 128)
					community.thumbnail = img.resize(image, 48, 48)
					if not community.image_version:
						community.image_version = 1
					else:
						memcache.delete('/images/community/avatar/%s/%d' % (community.key().id(), community.image_version))
						memcache.delete('/images/community/thumbnail/%s/%d' % (community.key().id(), community.image_version))
						community.image_version += 1
					memcache.delete('/images/community/avatar/%s' % community.key().id())
					memcache.delete('/images/community/thumbnail/%s' % community.key().id())
				if self.get_param('all_users'):
					community.all_users = True
				else:
					community.all_users = False
				category = model.Category.get(self.request.get('category'))
				prev_category = community.category
				community.category = category
				community.put()
				
				if prev_category:
					prev_category.communities -= 1
					prev_category.put()
				
				category.communities += 1
				category.put()
				
				memcache.delete('index_communities')
				self.redirect('/module/community/%s' % (community.url_path, ))
			else:
				# new community
				title = self.get_param('title')
				url_path = '-'
				all_users = False
				if self.get_param('all_users'):
					all_users = True
				community = model.Community(owner=user,
					owner_nickname=user.nickname,
					title=title,
					description=self.get_param('description'),
					url_path=url_path,
					members=1,
					all_users = all_users,
					articles=0,
					threads=0,
					responses=0,
					subscribers=[user.email],
					activity=1)
				category = model.Category.get(self.request.get('category'))
				community.category = category
				image = self.request.get("img")
				if image:
					image = images.im_feeling_lucky(image, images.JPEG)
					community.avatar = img.resize(image, 128, 128)
					community.thumbnail = img.resize(image, 48, 48)
					community.image_version = 1
				
				community.put()
				self.add_user_subscription(user, 'community', community.key().id())
				community.url_path = '%d/%s' % (community.key().id(), self.to_url_path(community.title))
				community.put()
				
				category.communities += 1
				category.put()
				
				user.communities += 1
				user.put()
				
				app = model.Application.all().get()
				if app:
					app.communities += 1
					app.put()
				memcache.delete('app')
				
				community_user = model.CommunityUser(user=user,
					community=community,
					user_nickname=user.nickname,
					community_title=community.title,
					community_url_path=community.url_path)
				community_user.put()
				memcache.delete('index_communities')
				
				followers = list(self.get_followers(user=user))
				followers.append(user.nickname)
				self.create_event(event_type='community.new', followers=followers, user=user, community=community)
				
				self.add_follower(community=community, nickname=user.nickname)
				
				# TODO: update a user counter to know how many communities is owner of?
				

				self.redirect('/module/community/%s' % (community.url_path, ))