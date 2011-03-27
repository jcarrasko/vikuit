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

from google.appengine.ext import db
from google.appengine.api import mail
from handlers.AuthenticatedHandler import *

class ArticleComment(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		key = self.get_param('key')
		article = model.Article.get(key)
		memcache.delete(str(article.key().id()) + '_article')
		if not article or article.draft or article.deletion_date:
			self.not_found()
			return
		
		if not self.auth():
			return

		content = self.get_param('content')
		if not content:
			self.show_error("Content is mandatory")
			return
		preview = self.get_param('preview')
		if preview:
			comment = model.Comment(article=article,
				author=user,
				author_nickname=user.nickname,
				content=content)
			self.values['comment'] = comment
			self.values['preview'] = True
			self.render('templates/module/article/article-comment-edit.html')
			return
		
		if self.check_duplicate(article, user, content):
			self.show_error("Duplicated comment")
			return
		# migration
		if not article.subscribers:
			com = [c.author.email for c in model.Comment.all().filter('article', article).fetch(1000) ]
			com.append(article.author.email)
			article.subscribers = list(set(com))
		# end migration

		comment = model.Comment(article=article,
			author=user,
			author_nickname=user.nickname,
			content=content,
			editions = 0,
			response_number=article.responses+1)
		comment.put()
		results = 10
		app = self.get_application()
		if app.max_results_sublist:
			results = app.max_results_sublist
		page = comment.response_number / results
		if (comment.response_number % results) > 0:
			page += 1
		comment_url = '/module/article/%s?p=%d#comment-%d' % (article.url_path, page, comment.response_number)
		
		user.comments += 1
		user.put()
		
		article.responses += 1
		article.put()
		
		followers = list(self.get_followers(user=user))
		followers.append(user.nickname)
		followers.extend(self.get_followers(article=article))
		followers = list(set(followers))
		self.create_event(event_type='article.comment',
			followers=followers, user=user, article=article, response_number=comment.response_number)
		memcache.add(str(article.key().id()) + '_article', article, 0)
		subscribers = article.subscribers
		if subscribers and user.email in subscribers:
			subscribers.remove(user.email)

		if subscribers:
			subject = self.getLocale("New comment in: '%s'") % self.clean_ascii(article.title)
			#Nuevo comentario en el artículo: '%s':\n%s%s\n\nTodos los comentarios en:\n%s/module/article/%s#comments\n\nEliminar suscripción a este artículo:\n%s/module/article.comment.subscribe?key=%s\n
			body =  self.getLocale("New comment in article: '%s':\n%s%s\n\nAll comments at:\n%s/module/article/%s#comments\n\nUnsuscribe this article:\n%s/module/article.comment.subscribe?key=%s\n") % (self.clean_ascii(article.title), app.url, comment_url, app.url, article.url_path, app.url, str(article.key()))
			self.mail(subject=subject, body=body, bcc=subscribers)
			
		subscribe = self.get_param('subscribe')
		if subscribe and not user.email in article.subscribers:
			article.subscribers.append(user.email)
		
		self.redirect(comment_url)
		
	def check_duplicate(self, article, user, content):
		last_comment = model.Comment.all().filter('article', article).filter('author', user).order('-creation_date').get()
		if last_comment is not None:
			if last_comment.content == content:
				return True
		return False
		
