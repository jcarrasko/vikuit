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

class AdminCategoryEdit(AuthenticatedHandler):

	def execute(self):
		method = self.request.method
		user = self.values['user']
		self.values['tab'] = '/admin'

		if user.rol != 'admin':
			self.forbidden()
			return
			
		key = self.get_param('key')
		self.values['parent_categories'] = list(model.Category.all().filter('parent_category', None).order('title'))
		self.values['parent_category'] = None

		if method == 'GET':
			if key:
				# show edit form
				category = model.Category.get(key)
				self.values['key'] = key

				self.values['title'] = category.title
				self.values['description'] = category.description
				self.values['parent_category'] = str(category.parent_category.key())
				self.render('templates/module/admin/admin-category-edit.html')
			else:
				# show an empty form
				self.values['key'] = None
				self.values['title'] = "New category"
				self.values['description'] = "Description"
				self.render('templates/module/admin/admin-category-edit.html')
		elif self.auth():
			title = self.get_param('title')
			desc = self.get_param('description')
			if title is None or len(title.strip()) == 0 or desc is None or len(desc.strip()) == 0:
				self.values['m'] = "Title and description are mandatory fields"
				self.values['key'] = key
				self.values['title'] = title
				self.values['description'] = desc
				self.values['parent_category'] = self.request.get('parent_category')
				self.render('templates/module/admin/admin-category-edit.html')
				return
			
			if key:
				# update category
				category = model.Category.get(key)
				category.title = self.get_param('title')
				category.description = self.get_param('description')
				category.url_path = self.to_url_path(category.title)
				parent_key = self.request.get('parent_category')
				if parent_key:
					category.parent_category = model.Category.get(parent_key)
				category.put()
				self.redirect('/module/admin.categories')
			else:
				category = model.Category(title=self.get_param('title'),
					description=self.get_param('description'),
					articles = 0,
					communities = 0)
				category.url_path = self.to_url_path(category.title)
				parent_key = self.request.get('parent_category')
				if parent_key:
					category.parent_category = model.Category.get(parent_key)
				category.put()
				self.redirect('/module/admin.categories')