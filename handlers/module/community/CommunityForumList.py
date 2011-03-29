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

class CommunityForumList(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/community.list'
		url_path = self.request.path.split('/', 3)[3]
		community = model.Community.gql('WHERE url_path=:1', url_path).get()
		if not community:
			self.not_found()
			return

		self.values['community'] = community
		self.values['joined'] = self.joined(community)
		if community.all_users is None or community.all_users:
			self.values['can_write'] = True
		else:
			self.values['can_write'] = self.can_write(community)
		query = model.Thread.all().filter('community', community).filter('parent_thread', None)
		threads = self.paging(query, 20, '-last_response_date', community.threads, ['-last_response_date'])
		self.values['threads'] = threads
		self.render('templates/module/community/community-forum-list.html')