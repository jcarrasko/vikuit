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


class ArticleCommentSubscribe( AuthenticatedHandler ):

	def execute(self):
		key  = self.get_param('key')
		article = model.Article.get(key)
		memcache.delete(str(article.key().id()) + '_article')
		user = self.values['user']
		mail = user.email
		
		if not mail in article.subscribers:
			if not self.auth():
				return
			article.subscribers.append(mail)
			article.put()
			self.add_user_subscription(user, 'article', article.key().id())
			memcache.add(str(article.key().id()) + '_article', article, 0)
			if self.get_param('x'):
				self.render_json({ 'action': 'subscribed' })
			else:
				self.redirect('/module/article/%s' % (article.url_path, ))
		else:
			auth = self.get_param('auth')
			if not auth:
				memcache.add(str(article.key().id()) + '_article', article, 0)
				self.values['article'] = article
				self.render('templates/module/article/article-comment-subscribe.html')
			else:
				if not self.auth():
					return
				article.subscribers.remove(mail)
				article.put()
				self.remove_user_subscription(user, 'article', article.key().id())
				memcache.add(str(article.key().id()) + '_article', article, 0)
				if self.get_param('x'):
					self.render_json({ 'action': 'unsubscribed' })
				else:
					self.redirect('/module/article/%s' % (article.url_path, ))

