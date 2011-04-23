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

class ArticleDelete(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		article = model.Article.get(self.get_param('key'))
		memcache.delete(str(article.key().id()))
		if not article:
			self.not_found()
			return
		
		if user.rol != 'admin' and user.nickname != article.author.nickname:
			self.forbidden()
			return

		if method == 'GET':
			self.values['article'] = article
			self.render('templates/module/article/article-delete.html')
		elif self.auth():
			# mark as deleted
			article.deletion_message = self.get_param('message')
			article.deletion_date = datetime.datetime.now()
			article.deletion_user = user
			article.put()
			
			# decrement tag counters
			self.delete_tags(article.tags)
			
			# decrement author counters
			if article.draft:
				article.author.draft_articles -= 1
			else:
				article.author.articles -=1
			article.author.rating_total -= article.rating_total
			article.author.rating_count -= article.rating_count
			if article.author.rating_count > 0:
				article.author.rating_average = int(article.author.rating_total / article.author.rating_count)
			else:
				article.author.rating_average = 0
			article.author.put()
			
			# decrement community counters and delete relationships
			gi = model.CommunityArticle.all().filter('article =', article)
			for g in gi:
				g.community.articles -= 1
				if g.community.activity:
					g.community.activity -= 15
				g.community
				g.community.put()
				g.delete()
			
			# decrement favourites and delete relationships
			fv = model.Favourite.all().filter('article =', article)
			for f in fv:
				f.user.favourites -= 1
				f.user.put()
				f.delete()
			
			
			rc = model.Recommendation.all().filter('article_from', article)
			for r in rc:
				r.delete()
				
			rc = model.Recommendation.all().filter('article_to', article)
			for r in rc:
				r.delete()
			
			# decrement votes and delete relationships
			# vt = model.Vote.all().filter('article =', article)
			# for v in vt:
			#	v.delete()
			
			# comments?
			memcache.delete('index_articles')
			app = model.Application.all().get()
			if app:
				app.articles -= 1
				app.put()
			memcache.delete('app')
			
			self.redirect('/module/article/%s' % article.url_path)
			