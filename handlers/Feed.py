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
import model
import datetime
import markdown

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from time import strftime, gmtime, time

from utilities.AppProperties import AppProperties

class Feed(webapp.RequestHandler):

	def get(self):
		data = memcache.get(self.request.path)
		if not data:
			time = 600
			params = self.request.path.split('/', 4)

			if not params[2]:
				latest = model.Article.gql('WHERE draft=:1 AND deletion_date=:2 ORDER BY creation_date DESC LIMIT 20', False, None)
				data = self.to_rss(self.get_application().name, latest)
			
			elif params[2] == 'mblog':
				query = model.Mblog.all().filter('deletion_date', None).order('-creation_date')
				latest = [o for o in query.fetch(25)]
				data = self.posts_to_rss(self.getLocale("Microbblogging"), latest)
				time = 200
	
			elif params[2] == 'tag':
				query = model.Article.all().filter('deletion_date', None).filter('tags =', params[3]).order('-creation_date')
				latest = [o for o in query.fetch(10)]
				data = self.to_rss(self.getLocale("Articles labeled with %s") % params[3], latest)

			elif params[3] == 'community.forum':
				community = model.Community.gql('WHERE url_path=:1',params[4]).get()
				if not community:
					community = model.Community.gql('WHERE old_url_path=:1',params[4]).get()
				threads = model.Thread.gql('WHERE community=:1 ORDER BY creation_date DESC LIMIT 20', community)
				data = self.threads_to_rss(self.getLocale("Forum %s") % community.title, threads)

			elif params[3] == 'community':
				community = model.Community.gql('WHERE url_path=:1',params[4]).get()
				if not community:
					community = model.Community.gql('WHERE old_url_path=:1',params[4]).get()
				community_articles = model.CommunityArticle.gql('WHERE community=:1 ORDER BY creation_date DESC LIMIT 20', community)
				latest = [gi.article for gi in community_articles]
				data = self.to_rss(self.getLocale("Articles by community %s") % community.title, latest)

			elif params[3] == 'user':
				latest = model.Article.gql('WHERE author_nickname=:1 AND draft=:2 AND deletion_date=:3 ORDER BY creation_date DESC LIMIT 20', params[4], False, None)
				data = self.to_rss(self.getLocale("Articles by %s") % params[3], latest)
				
			else:
				data = self.not_found()
				
			memcache.add(self.request.path, data, time)
			
		self.response.headers['Content-Type'] = 'application/rss+xml'
		self.response.out.write(template.render('templates/feed.xml', data))
		
	
	def threads_to_rss(self, title, threads):
		articles = []
		url = self.get_application().url
		md = markdown.Markdown()
		for i in threads:
			article = {
				'title': i.title,
				'link': "%s/module/community.forum/%s" % (url, i.url_path),
				'description': md.convert(i.content),
				'pubDate': self.to_rfc822(i.creation_date),
				'guid':"%s/module/community.forum/%s" % (url,i.url_path),
				'author': i.author_nickname
				# guid como link para mantener compatibilidad con feed.xml
			}
			articles.append(article)

		values = {
			'title': title,
			'self': url+self.request.path,
			'link': url,
			'description': '',
			'articles': articles
		}
		return values

	def posts_to_rss(self, title, list):
		posts = []
		url = self.get_application().url
		for i in list:
			post = {
				'title': "%s" % i.content,
				'link': "%s/module/mblog.edit/%s" % (url, i.key().id()),
				'description': "%s" % i.content,
				'pubDate': self.to_rfc822(i.creation_date),
				'guid':"%s/module/mblog.edit/%s" % (url,i.key().id()),
				'author': i.author_nickname
			}
			posts.append(post)

		values = {
			'title': title,
			'self': url+self.request.path,
			'link': url,
			'description': '%s Microbblogging' % self.get_application().name,
			'articles': posts
		}
		return values

	def to_rss(self, title, latest):
		import MediaContentFilters as contents
		articles = []
		url = self.get_application().url
		md = markdown.Markdown()
		for i in latest:
			if i.author.not_full_rss:
				content = md.convert(i.description)
			else:
				content = md.convert(i.content)
				content = contents.media_content(content)
			article = {
				'title': i.title,
				'link': "%s/module/article/%s" % (url, i.url_path),
				'description': content,
				'pubDate': self.to_rfc822(i.creation_date),
				'guid':"%s/module/article/%d/" % (url, i.key().id()),
				'author': i.author_nickname
				
			}
			articles.append(article)
			
		values = {
			'title': title,
			'self': url+self.request.path,
			'link': url,
			'description': '',
			'articles': articles
		}
		return values
	
	def to_rfc822(self, date):
		return date.strftime("%a, %d %b %Y %H:%M:%S GMT")
		
	def get_application(self):
		app = memcache.get('app')
		import logging
		if not app:
			app = model.Application.all().get()
			memcache.add('app', app, 0)
		return app

	def not_found(self):
		url = self.get_application().url
		values = {
			'title': self.get_application().name,
			'self': url,
			'link': url,
			'description': '',
			'articles': ''
		}
		return values

	### i18n
	def getLocale(self, label):
		env = AppProperties().getJinjaEnv()
		t = env.get_template("/translator-util.html")
		return t.render({"label": label})
