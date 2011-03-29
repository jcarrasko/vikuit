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

class CommunityUserUnjoin(AuthenticatedHandler):

	def execute(self):
		user = self.values['user']
		community = model.Community.get(self.get_param('community'))
		if not community:
			self.not_found()
			return
		
		if not self.auth():
			return
		
		redirect = self.get_param('redirect')

		gu = model.CommunityUser.gql('WHERE community=:1 and user=:2', community, user).get()
		if gu and user != community.owner:
			self.create_community_subscribers(community)
			gu.delete()
			
			if user.email in community.subscribers:
				community.subscribers.remove(user.email)
			community.members -= 1
			if community.activity:
				community.activity -= 1
			community.put()
			self.remove_user_subscription(user, 'community', community.key().id())
			self.remove_follower(community=community, nickname=user.nickname)
			user.communities -= 1
			user.put()
		self.redirect(redirect)
