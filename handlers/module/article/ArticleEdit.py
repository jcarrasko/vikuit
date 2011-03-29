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
from google.appengine.api import memcache
from handlers.AuthenticatedHandler import *

class ArticleEdit(AuthenticatedHandler):

	def execute(self):
		self.values['tab'] = '/module/article.list'
		method = self.request.method
		user = self.values['user']
		key = self.get_param('key')
		x = self.get_param('x')
		draft = False
		if self.get_param('save_draft'):
			draft = True
		
		licenses = [ { 'id': 'copyright', 'lic': '&copy; Todos los derechos reservados' },
			{ 'id': 'pd', 'lic': u'Dominio público' },
			{ 'id': 'by', 'lic': 'Creative Commons: Reconocimiento' },
			{ 'id': 'by-nc', 'lic': 'Creative Commons: Reconocimiento-No comercial' },
			{ 'id': 'by-nc-nd', 'lic': 'Creative Commons: Reconocimiento-No comercial-Sin obras derivadas' },
			{ 'id': 'by-nc-sa', 'lic': 'Creative Commons: Reconocimiento-No comercial-Compartir bajo la misma licencia' },
			{ 'id': 'by-nd', 'lic': 'Creative Commons: Reconocimiento-Sin obras derivadas' },
			{ 'id': 'by-sa', 'lic': 'Creative Commons: Reconocimiento-Compartir bajo la misma licencia' }
		]
		self.values['licenses'] = licenses
		
		if method == 'GET':
			if key:
				# show edit form
				article = model.Article.get(key)
				if not article:
					self.not_found()
					return
				if not user.nickname == article.author.nickname and user.rol != 'admin':
					self.forbidden()
					return
				self.values['key'] = key
				
				self.values['title'] = article.title
				self.values['lic'] = article.lic
				self.values['tags'] = ', '.join(article.tags)
				self.values['description'] = article.description
				self.values['content'] = article.content
				self.values['draft'] = article.draft
				self.render('templates/module/article/article-edit.html')
			else:
				# show an empty form
				self.values['title'] = u'Título...'
				self.values['lic'] = 'copyright'
				self.values['draft'] = True
				self.render('templates/module/article/article-edit.html')
		elif self.auth():
			if x and draft:
				# check mandatory fields
				if not self.get_param('title') or not self.get_param('tags') or not self.get_param('description') or not self.get_param('content'):
					self.render_json({ 'saved': False })
					return
			if key:
				# update article
				article = model.Article.get(key)
				memcache.delete(str(article.key().id()) + '_html')
				if not article:
					self.not_found()
					return
				if not user.nickname == article.author.nickname and user.rol != 'admin':
					self.forbidden()
					return
				
				lic = self.get_param('lic')
				lics = [license['id'] for license in licenses]
				if not lic in lics:
					lic = 'copyright'
				
				if not article.draft:
					self.delete_tags(article.tags)
				article.lic = lic
				article.tags = self.parse_tags(self.get_param('tags'))
				article.description = ' '.join(self.get_param('description').splitlines())
				article.content = self.get_param('content')
				if article.draft:
					# title and url_path can change only if the article hasn't already been published
					article.title = self.get_param('title')
					article.url_path = '%d/%s' % (article.key().id(), self.to_url_path(article.title))
				add_communities = False
				if article.draft and not draft:
					article.draft = draft
					user.articles += 1
					user.draft_articles -=1
					user.put()
					article.creation_date = datetime.datetime.now()
					self.add_follower(article=article, nickname=user.nickname)
					followers = list(self.get_followers(user=user))
					followers.append(user.nickname)
					self.create_event(event_type='article.new', followers=followers, user=user, article=article)
					
					app = model.Application.all().get()
					if app:
						app.articles += 1
						app.put()
					memcache.delete('app')
					add_communities = True
				
				if not article.draft:
					self.create_recommendations(article)
				
				if not article.author_nickname:
					article.author_nickname = user.nickname
				
				if not article.content_html:	
					html = model.ArticleHtml(content=article.content)
					html.put()
					article.content_html = html
				else:
					html_content = article.content
					html_content = self.media_content(html_content)
					article.content_html.content = html_content
					article.content_html.put()
				
				article.put()
				
				memcache.delete('index_articles')
				memcache.delete('tag_cloud')
				memcache.delete(str(article.key().id()))
				
				if not draft:
					self.update_tags(article.tags)
				if x:
					self.render_json({ 'saved': True, 'key' : str(article.key()), 'updated' : True, "draft_articles" : str(user.draft_articles) })
				else:
					if add_communities:
						self.redirect('/module/article.add.communities?key=%s' % str(article.key()))
					else:
						self.redirect('/module/article/%s' % article.url_path)
			else:
				# new article
				today = datetime.date.today()
				title = self.get_param('title')
				tags = self.parse_tags(self.get_param('tags'))
				
				lic = self.get_param('lic')
				lics = [license['id'] for license in licenses]
				if not lic in lics:
					lic = 'copyright'
				
				article = model.Article(author=user,
					author_nickname=user.nickname,
					title=title,
					description=' '.join(self.get_param('description').splitlines()),
					content=self.get_param('content'),
					lic=lic,
					url_path='empty',
					tags=tags,
					draft=draft,
					article_type='article',
					views=0,
					responses=0,
					rating_count=0,
					rating_total=0,
					favourites=0)
		
				html_content = article.content
				
				html = model.ArticleHtml(content=self.media_content(html_content))
				html.put()
				article.content_html = html
				article.subscribers = [user.email]
				article.put()
				
				self.add_user_subscription(user, 'article', article.key().id())
				article.url_path = '%d/%s' % (article.key().id(), self.to_url_path(article.title))
				article.put()
				
				memcache.delete('index_articles')
				memcache.delete('tag_cloud')
				memcache.delete(str(article.key().id()))
				
				if not draft:
					self.create_recommendations(article)
					user.articles += 1
					user.put()
					self.update_tags(tags)
					self.add_follower(article=article, nickname=user.nickname)
					followers = list(self.get_followers(user=user))
					followers.append(user.nickname)
					self.create_event(event_type='article.new', followers=followers, user=user, article=article)
					app = model.Application.all().get()
					if app:
						app.articles += 1
						app.put()
						memcache.delete('app')
				else:
					user.draft_articles += 1
					user.put()
				
				if x:
					self.render_json({ 'saved': True, 'key' : str(article.key()), "updated" : False, "draft_articles" : str(user.draft_articles) })
				else:
					if article.draft:
						self.redirect('/module/article/%s' % article.url_path)
					else:
						self.redirect('/module/article.add.communities?key=%s' % str(article.key()))
	
	def create_recommendations(self, article):
		self.create_task('article_recommendation', 1, {'article': article.key().id(), 'offset': 0})
