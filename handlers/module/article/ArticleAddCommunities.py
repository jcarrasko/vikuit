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

from handlers.AuthenticatedHandler import *

class ArticleAddCommunities(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		key = self.get_param('key')
		article = model.Article.get(key)
		if not article or article.draft or article.deletion_date:
			self.not_found()
			return
		if not user.nickname == article.author.nickname:
			self.forbidden()
			return
		
		if method == 'GET':
			self.values['key'] = key
			self.values['article'] = article
			communities = list(model.CommunityUser.all().filter('user', user).order('community_title'))
			self.values['communities'] = communities
			if not communities:
				self.redirect('/module/article/%s' % article.url_path)
				return
			self.render('templates/module/article/article-add-communities.html')
		elif self.auth():
			arguments = self.request.arguments()
			for gu in model.CommunityUser.all().filter('user', user).order('community_title'):
				community = gu.community
				if self.request.get('community-%d' % community.key().id()):
					gi = model.CommunityArticle.all().filter('community', community).filter('article', article).count(1)
					if not gi:
						community.articles += 1
						if community.activity:
							community.activity += 15
						community.put()
						gi = model.CommunityArticle(community=community,
							article=article,
							article_author_nickname = article.author_nickname,
							article_title = article.title,
							article_url_path = article.url_path,
							community_title = community.title,
							community_url_path = community.url_path)
						gi.put()
						
						followers = list(self.get_followers(community=community))
						self.create_event(event_type='community.addarticle', followers=followers, user=user, community=community, article=article)
						
			self.redirect('/module/article/%s' % article.url_path)