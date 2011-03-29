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

import logging
from google.appengine.api import mail
from handlers.AuthenticatedHandler import *
from google.appengine.runtime import apiproxy_errors

class CommunityNewArticle(AuthenticatedHandler):

	def execute(self):
		article = model.Article.get(self.get_param('article'))
		community = model.Community.get(self.get_param('community'))
		if not community or not article or article.draft or article.deletion_date:
			self.not_found()
			return
		
		if not self.auth():
			return
		
		user = self.values['user']
		gu = self.joined(community)
		if gu and not article.draft:
			gi = model.CommunityArticle.gql('WHERE community=:1 and article=:2', community, article).get()
			if not gi and user.nickname == article.author.nickname:
				gi = model.CommunityArticle(article=article,
					community=community,
					article_author_nickname=article.author_nickname,
					article_title=article.title,
					article_url_path=article.url_path,
					community_title=community.title,
					community_url_path=community.url_path)
				gi.put()
				
				community.articles += 1
				if community.activity:
					community.activity += 15
				community.put()
				
				followers = list(self.get_followers(community=community))
				self.create_event(event_type='community.addarticle', followers=followers, user=user, community=community, article=article)
				
				subscribers = community.subscribers
				if subscribers and user.email in subscribers:
					subscribers.remove(user.email)
					
				if subscribers:
					app = self.get_application()
					subject = self.getLocale("New article: '%s'") % self.clean_ascii(article.title) # u"Nuevo articulo: '%s'"

					body = self.getLocale("New article at community %s.\nArticle title: %s\nRead more at:\n%s/module/article/%s\n") % (self.clean_ascii(community.title), self.clean_ascii(article.title), app.url, article.url_path)
					self.mail(subject=subject, body=body, bcc=community.subscribers)
				
		self.redirect('/module/article/%s' % article.url_path)
