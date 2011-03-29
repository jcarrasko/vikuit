#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>
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

from handlers.BaseHandler import *

class MainPage(BaseHandler):

	def execute(self):
		self.values['tab'] = '/'
		# memcache.delete('index_articles')
		# memcache.delete('index_communities')
		# memcache.delete('index_threads')
		self.values['articles'] = self.cache('index_articles', self.get_articles)
		# self.values['communities'] = self.cache('index_communities', self.get_communities)
		self.values['threads'] = self.cache('index_threads', self.get_threads)
		self.add_tag_cloud()
		# self.add_categories()
		self.render('templates/index.html')
		
	def get_articles(self):
		return model.Article.all().filter('draft', False).filter('deletion_date', None).order('-creation_date').fetch(5)
		# return self.render_chunk('templates/index-articles.html', {'articles': articles})

	def get_communities(self):
		return model.Community.all().order('-members').fetch(5)
		# return self.render_chunk('templates/index-communities.html', {'communities': communities})

	def get_threads(self):
		return model.Thread.all().filter('parent_thread', None).order('-last_response_date').fetch(5)
		# return self.render_chunk('templates/index-threads.html', {'threads': threads})
