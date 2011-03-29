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

class CommunityView(BaseHandler):

	def execute(self):
		self.values['tab'] = '/module/community.list'
		url_path = self.request.path.split('/', 3)[3]
		community = model.Community.gql('WHERE url_path=:1', url_path).get()
		if not community:
			community = model.Community.gql('WHERE old_url_path=:1', url_path).get()
			if community:
				self.redirect('/module/community/%s' % community.url_path, permanent=True)
				return
			self.not_found()
			return

		self.values['community'] = community
		self.values['joined'] = self.joined(community)
		self.values['articles'] = list(model.CommunityArticle.all().filter('community', community).order('-creation_date').fetch(5))
		self.values['threads'] = list(model.Thread.all().filter('community', community).filter('parent_thread', None).order('-last_response_date').fetch(5))
		self.values['users'] = list(model.CommunityUser.all().filter('community', community).order('-creation_date').fetch(27))
		self.values['related'] = list(model.RelatedCommunity.all().filter('community_from', community).order('-creation_date').fetch(10))
		self.render('templates/module/community/community-view.html')