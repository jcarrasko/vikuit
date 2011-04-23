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

class CommunityUserJoin(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		community = model.Community.get(self.get_param('community'))
		if not community:
			self.not_found()
			return
		
		if not self.auth():
			return
		
		redirect = self.get_param('redirect')
		
		gu = self.joined(community)
		if gu == 'False':
			self.create_community_subscribers(community)
			
			gu = model.CommunityUser(user=user,
				community=community,
				user_nickname=user.nickname,
				community_title=community.title,
				community_url_path=community.url_path)
			gu.put()
			
			community.subscribers.append(user.email)
			community.members += 1
			if community.activity:
				community.activity += 1
			community.put()
			
			self.add_follower(community=community, nickname=user.nickname)
			
			self.add_user_subscription(user, 'community', community.key().id())
			user.communities += 1
			user.put()
		self.redirect(redirect)
