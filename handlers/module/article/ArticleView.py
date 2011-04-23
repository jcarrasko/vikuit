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
from handlers.BaseHandler import *


class ArticleView(BaseHandler):

	def execute(self):
		url_path = self.request.path.split('/', 3)[3]
		article_id = self.request.path.split('/')[3]
		article = self.cache(article_id + '_article', self.get_article)
		
		if not article:
			self.not_found()
			return
		
		if article.url_path != url_path:
			self.redirect('/module/article/%s' % article.url_path, permanent=True)
			return

		if not article.author_nickname:
			article.author_nickname = article.author.nickname
			article.put()
		
		user = self.values['user']
		if article.deletion_date and (not user or (user.rol != 'admin' and article.author_nickname != user.nickname)):
			self.values['article'] = article
			self.error(404)
			self.render('templates/module/article/article-deleted.html')
			return
		
		self.values['tab'] = '/module/article.list'
		
		if article.draft and (not user or not user.nickname == article.author_nickname):
			self.not_found()
			return


		if user and user.nickname != article.author_nickname:
			vote = model.Vote.gql('WHERE user=:1 AND article=:2', user, article).get()
			if not vote:
				self.values['canvote'] = True
		if user:
			added = model.Favourite.gql('WHERE user=:1 AND article=:2',user,article).get()
			if not added:
				self.values['canadd'] = True
		if user:
			if user.email in article.subscribers:
				self.values['cansubscribe'] = False
			else:
				self.values['cansubscribe'] = True

		
		self.values['article'] = article
		results = 10
		app = self.get_application()
		if app.max_results_sublist:
			results = app.max_results_sublist
		query = model.Comment.all().filter('article =', article)
		comments = self.paging(query, results, 'creation_date', article.responses, 'creation_date')
		# migration
		i = 1
		for c in comments:
			if not c.author_nickname:
				c.author_nickname = c.author.nickname
				c.put()
			if not c.response_number:
				c.response_number = i
				c.put()
			i += 1
		# end migration
		self.values['comments'] = comments
		self.values['a'] = 'comments'
		self.values['keywords'] = ', '.join(article.tags)
		
		communities = model.CommunityArticle.all().filter('article', article).order('community_title')
		# communities = self.cache(str(article.key().id()) + '_communities', self.get_communities)
		self.values['communities'] = list(communities)
		
		if user and article.author_nickname == user.nickname:
			all_communities = list(model.CommunityUser.all().filter('user', user).order('community_title'))
			
			# TODO: this could be improved
			for g in communities:
				for gr in all_communities:
					if gr.community_url_path == g.community_url_path:
						all_communities.remove(gr)
				
			if all_communities:
				self.values['all_communities'] = all_communities

		self.values['content_html'] = self.cache(str(article.key().id()) + '_html', self.to_html)
		
		self.values['related'] = list(model.Recommendation.all().filter('article_from', article).order('-value').fetch(5))

		self.render('templates/module/article/article-view.html')
	
	def to_html(self):
		article = self.values['article']
		if not article.content_html:
			html = model.ArticleHtml(content=self.markdown(article.content))
			html = model.ArticleHtml(content=self.media_content(article.content))
			html.put()
			article.content_html = html
			article.put()
		return article.content_html.content
		
	def get_communities(self):
		article = self.values['article']
		return model.CommunityArticle.all().filter('article', article).order('community_title')
		
	def get_author(self):
		article = self.values['article']
		return model.UserData.all().filter('nickname', article.author_nickname).get()
		
	def get_article(self):
		article_id = self.request.path.split('/')[3]
		return model.Article.get_by_id(int(article_id))
