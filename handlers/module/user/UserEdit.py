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

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class UserEdit(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']

		if method == 'GET':
			self.values['google_adsense'] = self.not_none(user.google_adsense)
			self.values['google_adsense_channel'] = self.not_none(user.google_adsense_channel)
			self.values['real_name'] = self.not_none(user.real_name)
			self.values['links'] = [(link.split('##', 2)[1], link.split('##', 2)[0]) for link in user.list_urls]
			self.values['im_addresses'] =  [(link.split('##', 2)[1], link.split('##', 2)[0]) for link in user.im_addresses]
			self.values['country'] = self.not_none(user.country)
			self.values['city'] = self.not_none(user.city)
			self.values['about'] = self.not_none(user.about_user)
			self.values['personal_message'] = self.not_none(user.personal_message);
			if user.not_full_rss:
				self.values['not_full_rss'] = user.not_full_rss
			self.render('templates/module/user/user-edit.html')
		elif self.auth():
			user.google_adsense = self.get_param('google_adsense')
			user.google_adsense_channel = self.get_param('google_adsense_channel')
			user.real_name = self.get_param('real_name')
			user.personal_message = self.get_param('personal_message')
			user.country = self.get_param('country')
			if self.get_param('not_full_rss'):
				user.not_full_rss = True
			else:
				user.not_full_rss = False
			image = self.request.get("img")
			if image:
				image = images.im_feeling_lucky(image, images.JPEG)
				user.avatar = img.resize(image, 128, 128)
				user.thumbnail = img.resize(image, 48, 48)
				if not user.image_version:
					user.image_version = 1
				else:
					memcache.delete('/images/user/avatar/%s/%d' % (user.nickname, user.image_version))
					memcache.delete('/images/user/thumbnail/%s/%d' % (user.nickname, user.image_version))
					user.image_version += 1
				memcache.delete('/images/user/avatar/%s' % (user.nickname))
				memcache.delete('/images/user/thumbnail/%s' % (user.nickname))
			user.city = self.get_param('city')
			user.list_urls = []
			blog = self.get_param('blog')
			if blog:
				if not blog.startswith('http'):
					linkedin = 'http://' + blog
				user.list_urls.append(blog + '##blog')
				
			linkedin = self.get_param('linkedin')
			if linkedin:
				if not linkedin.startswith('http'):
					linkedin = 'http://' + linkedin
				user.list_urls.append(linkedin + '##linkedin')
				
			ohloh = self.get_param('ohloh')
			if ohloh:
				if not ohloh.startswith('http'):
					linkedin = 'http://' + ohloh
				user.list_urls.append(ohloh + '##ohloh')
				
			user.im_addresses = []
			msn = self.get_param('msn')
			if msn:
				user.im_addresses.append(msn + '##msn')
				
			jabber = self.get_param('jabber')
			if jabber:
				user.im_addresses.append(jabber + '##jabber')
				
			gtalk = self.get_param('gtalk')
			if gtalk:
				user.im_addresses.append(gtalk + '##gtalk')
				
			user.about_user = self.get_param('about_user')
			user.put()
			
			followers = list(self.get_followers(user=user))
			followers.append(user.nickname)
			self.create_event(event_type='user.edit', followers=followers, user=user)
			
			self.redirect('/module/user/%s' % user.nickname)
		
		
		
