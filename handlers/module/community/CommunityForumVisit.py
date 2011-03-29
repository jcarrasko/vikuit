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

class CommunityForumVisit(BaseRest):

	def get(self):
		thread_id = self.request.get('id')
		memcache.delete(thread_id + '_thread')
		thread = model.Thread.get_by_id(int(thread_id))
		thread.views += 1
		thread.put()
		memcache.add(str(thread.key().id()) + '_thread', thread, 0)
		content = []
		self.render_json({'views' : thread.views})
		return