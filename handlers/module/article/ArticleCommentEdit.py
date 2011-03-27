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

class ArticleCommentEdit(AuthenticatedHandler):

	def execute(self):
		self.values['tab'] = '/module/article.list'
		method = self.request.method
		user = self.values['user']
		comment_key = self.get_param('key')

		if method == 'GET':
			if comment_key:
				# show edit form
				comment = model.Comment.get(comment_key)
				if user.nickname != comment.author_nickname and user.rol != 'admin':
					self.forbidden()
					return
				if comment is None:
					self.not_found()
					return
				self.values['article'] = comment.article
				self.values['comment'] = comment
				self.values['comment_key'] = comment.key
				self.render('templates/module/article/article-comment-edit.html')
				return
			else:
				self.show_error("Comment not found")
				return
		elif self.auth():
			if comment_key:
				# update comment
				comment = model.Comment.get(comment_key)
				if user.nickname != comment.author_nickname and user.rol != 'admin':
					self.forbidden()
					return
					
				if not comment:
					self.not_found()
					return
				content = self.get_param('content')
				if not content:
					self.values['article'] = comment.article
					self.values['comment'] = comment
					self.values['comment_key'] = comment.key
					self.values['m'] = "Content is mandatory"
					self.render('templates/module/article/article-comment-edit.html')
					return
				comment.content = content
				if user.rol != 'admin':
					if comment.editions is None:
						comment.editions = 0
					comment.editions +=1
					comment.last_edition = datetime.datetime.now()
				comment.put()
				results = 10
				app = self.get_application()
				if app.max_results_sublist:
					results = app.max_results_sublist
				page = comment.response_number / results
				if (comment.response_number % results) > 0:
					page += 1
				self.redirect('/module/article/%s?p=%d#comment-%s' % (comment.article.url_path, page, comment.response_number))
			else:
				self.show_error("Comment not found")
				return