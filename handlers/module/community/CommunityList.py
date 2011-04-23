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

class CommunityList(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/community.list'
		query = model.Community.all()
		key = '%s?%s' % (self.request.path, self.request.query)
		
		cat = self.get_param('cat')
		app = self.get_application()
		if cat:
			category = model.Category.all().filter('url_path', cat).get()
			self.values['category'] = category
			self.values['cat'] = cat
			query = query.filter('category', category)
			max = category.communities
		else:
			max = app.communities
		results = 10
		if app.max_results:
			results = app.max_results
		communities = self.paging(query, results, '-members', max, ['-creation_date', '-members', '-articles'], key)
		self.values['communities'] = communities
		# denormalization
		for g in communities:
			if not g.owner_nickname:
				g.owner_nickname = g.owner.nickname
				g.put()
		self.add_categories()
		self.add_tag_cloud()
		self.render('templates/module/community/community-list.html')
