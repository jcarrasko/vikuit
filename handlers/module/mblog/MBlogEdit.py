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

import time
import datetime
import re

from google.appengine.ext import db
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class MBlogEdit(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		key = self.get_param('key')
		action = self.get_param('act')
			
		if method == 'GET':
			if key:#Unused - This case is to allow edit a post and add comments in a single post page
				# show edit form
				post = model.Mblog.get_by_id(key)
				if not post:
					self.not_found()
					return
				if not user.nickname == post.author.nickname and user.rol != 'admin':
					self.forbidden()
					return
				self.values['key'] = key
				self.values['content'] = post.content
				self.render('templates/module/mblog/mblog-edit.html')
			else:
				self.not_found()
				return
		elif self.auth():
				# new post
				if not action:
					
					content = self.get_param('content')
					if not content or len(content) == 0:
						self.render_json({ 'saved': False, 'msg': self.getLocale('Content is empty') })
						return
					if len(content) > 150:
						self.render_json({ 'saved': False, 'msg': self.getLocale('Content is too large') })
						return
					if not re.match(u"^[A-Za-z0-9_-àáèéíòóúÀÁÈÉÍÒÓÚïü: ,=\./&¿\?!¡#\(\)]*$", content):
						self.render_json({ 'saved': False, 'msg': self.getLocale('Content is invalid') })
						return
					
					post = model.Mblog(author=user,
						author_nickname=user.nickname,
						content=content,
						responses=0)
					post.put()
					self.render_json({ "saved": True, 'key' : str(post.key()) })
					return
				elif action == 'del' and key:
					post = model.Mblog.get_by_id(long(key))
					if not post:
						self.render_json({ 'saved': False, 'msg': self.getLocale('Not found') })
						return
					if not user.nickname == post.author.nickname and user.rol != 'admin':
						self.render_json({ 'saved': False, 'msg': self.getLocale('Not allowed') })
						return
					post.deletion_date = datetime.datetime.now()
					post.deletion_user = user.nickname
					post.put()
					self.render_json({ 'saved': True })
					return
				else:
					self.render_json({ 'saved': False, 'msg': self.getLocale('Not found') })
					return
				#UPDATE CACHE
				
