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

class CommunityArticleDelete(AuthenticatedHandler):

	def execute(self):
		article = model.Article.get(self.get_param('article'))
		community = model.Community.get(self.get_param('community'))
		if not article or not community:
			self.not_found()
			return
		
		if not self.auth():
			return
		
		gi = model.CommunityArticle.gql('WHERE community=:1 and article=:2', community, article).get()
		if self.values['user'].nickname == article.author.nickname:
			gi.delete()
			community.articles -= 1
			if community.activity:
				community.activity -= 15
			community.put()
		self.redirect('/module/article/%s' % article.url_path)
