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

class CommunityAddRelated(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		self.values['tab'] = '/admin'

		if user.rol != 'admin':
			self.forbidden()
			return

		if method == 'GET':
			self.values['m'] = self.get_param('m')
			self.render('templates/module/community/community-add-related.html')
		elif self.auth():
			fromId = self.request.get('community_from')
			toId = self.request.get('community_to')
			
			if fromId is None or len(fromId.strip()) == 0 or not fromId.isdigit():
				self.values['m'] = "Enter a valid source community"
				self.render('templates/module/community/community-add-related.html')
				return
			if toId is None or len(toId.strip()) == 0:
				self.values['m'] = "Enter a valid target community"
				self.render('templates/module/community/community-add-related.html')
				return
			
			community_from = model.Community.get_by_id(int(fromId))
			community_to = model.Community.get_by_id(int(toId))
			
			related = model.RelatedCommunity.all().filter('community_from', community_from).filter('community_to', community_to).get()
			if related:
				self.redirect('/module/community.add.related?m=Already_exists')
				return
			
			if community_from is None:
				self.values['m'] = "Source community not found"
				self.render('templates/module/community/community-add-related.html')
				return
			if community_to is None:
				self.values['m'] = "Target community not found"
				self.render('templates/module/community/community-add-related.html')
				return
			
			self.create_related(community_from, community_to)
			self.create_related(community_to, community_from)
			
			self.redirect('/module/community.add.related?m=Updated')
	
	def create_related(self, community_from, community_to):
		related = model.RelatedCommunity(community_from = community_from,
			community_to = community_to,
			community_from_title = community_from.title,
			community_from_url_path = community_from.url_path,
			community_to_title = community_to.title,
			community_to_url_path = community_to.url_path)
		related.put()