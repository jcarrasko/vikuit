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

class ArticleVote(AuthenticatedHandler):
	
	def execute(self):
		article = model.Article.get(self.get_param('key'))
		if not article or article.draft or article.deletion_date:
			self.not_found()
			return
		
		if not self.auth():
			return
		memcache.delete(str(article.key().id()) + '_article')
		rating = int(self.get_param('rating'))
		if rating < 0:
			rating = 0
		elif rating > 5:
			rating = 5
		
		user = self.values['user']
		avg = article.rating_average
		
		if article and article.author.nickname != user.nickname:
			vote = model.Vote.gql('WHERE user=:1 and article=:2', user, article).get()
			if not vote:
				vote = model.Vote(user=user,rating=rating,article=article)
				vote.put()

				article.rating_count += 1
				article.rating_total += rating
				article.rating_average = int(article.rating_total / article.rating_count)
				article.put()

				author = article.author
				author.rating_count += 1
				author.rating_total += rating
				author.rating_average = int(author.rating_total / author.rating_count)
				author.put()
				avg = article.rating_average
		memcache.add(str(article.key().id()) + '_article', article, 0)
		
		if self.get_param('x'):
			self.render_json({ 'average': avg, 'votes': article.rating_count })
		else:
			self.redirect('/module/article/%s' % article.url_path)
