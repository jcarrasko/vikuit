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

from google.appengine.ext import db
from handlers.AuthenticatedHandler import *

class ArticleCommentDelete(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		if user.rol != 'admin':
			self.forbidden()
			return
		
		if not self.auth():
			return
		
		comment = model.Comment.get(self.get_param('key'))
		
		if not comment:
			self.not_found()
			return
		url = comment.article.url_path
		message = self.get_param('message')
		#decrement nomber of comments in the User
		comment.author.comments -= 1
		comment.author.put()
			
		#delete comment
		comment.deletion_date = datetime.datetime.now()
		comment.deletion_message = message
		comment.put()
		self.redirect('/module/article/%s' % url)
