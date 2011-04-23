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

class ArticleFavourite(AuthenticatedHandler):
	
	def execute(self):
		article = model.Article.get(self.get_param('key'))
		user = self.values['user']
		if not article or article.draft or article.deletion_date:
			self.not_found()
			return
		
		if not self.auth():
			return

		favourite = model.Favourite.gql('WHERE user=:1 AND article=:2', user, article).get()
		if not favourite:
			favourite = model.Favourite(article=article,
				user=user,
				article_author_nickname=article.author_nickname,
				article_title=article.title,
				article_url_path=article.url_path,
				user_nickname=user.nickname)
			favourite.put()

			user.favourites += 1
			user.put()
			
			followers = list(self.get_followers(user=user))
			followers.append(user.nickname)
			followers.extend(self.get_followers(article=article))
			followers = list(set(followers))
			self.create_event(event_type='article.favourite', followers=followers, user=user, article=article)
			
			if self.get_param('x'):
				self.render_json({ 'action': 'added' })
			else:
				self.redirect('/module/article/%s' % article.url_path)
		else:
			favourite.delete()
			
			user.favourites -= 1
			user.put()
		
			if self.get_param('x'):
				self.render_json({ 'action': 'deleted' })
			else:
				self.redirect('/module/article/%s' % article.url_path)
