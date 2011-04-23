#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Blanco <jose.blanco[a]vikuit.com>
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>

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

import model
import logging

from google.appengine.api import memcache
from google.appengine.ext import webapp

class ImageDisplayer(webapp.RequestHandler):

	def get(self):
		cached = memcache.get(self.request.path)
		
		params = self.request.path.split('/')
		if params[2] == 'user':
			user = model.UserData.gql('WHERE nickname=:1', params[4]).get()
			self.display_image(user, params, cached, 'user128_1.png', 'user48_1.png')
		elif params[2] == 'community':
			community = model.Community.get_by_id(int(params[4]))
			self.display_image(community, params, cached, 'community128.png', 'community48.png')
		elif params[2] == 'gallery':
			query = model.Image.gql('WHERE url_path=:1', '%s/%s' % (params[4], params[5]) )
			image = query.get()
			self.display_image(image, params, cached, 'unknown128.png', 'unknown48.png', False)
		elif params[2] == 'application':
			app = model.Application.all().get()
			image = app.logo
			self.display_image(image, params, cached, 'logo.gif', 'logo.gif', False)
		
		else:
			self.error(404)
			return
	
	def display_image(self, obj, params, cached, default_avatar, default_thumbnail, not_gallery=True):
		if obj is None:
			if not_gallery:
				self.error(404)
			else:
				self.redirect('/static/images/%s' % default_thumbnail)
			return
		image = None
		if cached:
			image = self.write_image(cached)
		else:
			if params[3] == 'avatar':
				image = obj.avatar
				if not image:
					self.redirect('/static/images/%s' % default_avatar)
					return
			elif params[3] == 'thumbnail':
				image = obj.thumbnail
				if not image:
					self.redirect('/static/images/%s' % default_thumbnail)
					return
			elif params[3] == 'logo':
				image = obj
				if not image:
					self.redirect('/static/images/%s' % default_thumbnail)
					return
		
		if not_gallery and (len(params) == 5 or not obj.image_version or int(params[5]) != obj.image_version):
			if not obj.image_version:
				obj.image_version = 1
				obj.put()
			newparams = params[:5]
			newparams.append(str(obj.image_version))
			self.redirect('/'.join(newparams))
			return
			# self.response.headers['Content-Type'] = 'text/plain'
			# self.response.out.write('/'.join(params))
		else:
			if not cached:
				memcache.add(self.request.path, image)
			self.write_image(image)
	
	def write_image(self, image):
		self.response.headers['Content-Type'] = 'image/jpg'
		self.response.headers['Cache-Control'] = 'public, max-age=31536000'
		self.response.out.write(image)

	def showImage(self, image, default):
		if image:
			self.write_image(image)
			memcache.add(self.request.path, image)
		else:
			self.redirect('/static/images/%s' % default)