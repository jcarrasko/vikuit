#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# (C) Copyright 2008 Alberto Gimeno <gimenete at gmail dot com>
# 
# This file is part of "debug_mode_on".
# 
# "debug_mode_on" is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# "debug_mode_on" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with "debug_mode_on".  If not, see <http://www.gnu.org/licenses/>.
# 

from handlers.BaseHandler import *

class ForumList(BaseHandler):

	def execute(self):
		self.values['tab'] = '/forum.list'
		query = model.Thread.all().filter('parent_thread', None)
		app = self.get_application()
		key = '%s?%s' % (self.request.path, self.request.query)
		results = 10
		if app.max_results:
			results = app.max_results
		threads = self.paging(query, results, '-last_response_date', app.threads, ['-last_response_date'], key)
		# migration
		for t in threads:
			if not t.last_response_date:
				last_response = model.Thread.all().filter('parent_thread', t).order('-creation_date').get()
				if last_response:
					t.last_response_date = last_response.creation_date
				else:
					t.last_response_date = t.creation_date
				t.put()
		# end migration
		self.values['threads'] = threads
		self.add_tag_cloud()
		self.render('templates/forum-list.html')
