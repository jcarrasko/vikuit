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

from handlers.BaseHandler import *

class ArticleList(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/article.list'
		query = model.Article.all().filter('draft =', False).filter('deletion_date', None)
		app = self.get_application()
		key = '%s?%s' % (self.request.path, self.request.query)
		results = 10
		if app.max_results:
			results = app.max_results
		self.values['articles'] = self.paging(query, results, '-creation_date', app.articles, ['-creation_date', '-rating_average', '-responses'], key)
		self.add_tag_cloud()
		self.render('templates/module/article/article-list.html')
