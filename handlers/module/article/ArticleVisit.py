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

from handlers.BaseRest import *

class ArticleVisit(BaseRest):

	def get(self):
		article_id = self.request.get('id')

		memcache.delete(article_id + '_article')
		article = model.Article.get_by_id(int(article_id))
		article.views += 1
		article.put()
		memcache.add(str(article.key().id()) + '_article', article, 0)
		content = []
		self.render_json("{\"views\" : "+str(article.views)+"}")
		return