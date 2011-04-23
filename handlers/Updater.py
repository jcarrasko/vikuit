#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>
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
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from handlers.BaseHandler import *
from utilities.AppProperties import AppProperties

# Params

UPDATER_VERSION = "0.8"


def	update():
	
	app = model.Application.all().get()
	
	if app is None:
		initializeDb()			
		#self.response.out.write('App installed. Created user administrator. nickname="admin", password="1234". Please change the password.')
		return
	elif not app.session_seed:	
				
		import sha, random
		app.session_seed = sha.new(str(random.random())).hexdigest()
		app.put()
		#self.response.out.write('Seed installed')

	version = app.version
	if version is None or  version != UPDATER_VERSION:
	
		update07to08()
		#self.response.out.write ('updated to version 0.8')
		# elif app.version == '0.8':
		# update08to09()
		# elif app.version == '0.9':
		# update09to10()
	return

def initializeDb():
	
		app = model.Application.all().get()
		
		if app is None:
			app = model.Application()
			app.name = 'vikuit-example'
			app.subject = 'Social portal: lightweight and easy to install'
			app.recaptcha_public_key = '6LdORAMAAAAAAL42zaVvAyYeoOowf4V85ETg0_h-'
			app.recaptcha_private_key = '6LdORAMAAAAAAGS9WvIBg5d7kwOBNaNpqwKXllMQ'
			app.theme = 'blackbook'
			app.users = 0
			app.communities = 0
			app.articles = 0
			app.threads = 0
			app.url = "http://localhost:8080"
			app.mail_subject_prefix = "[Vikuit]"
			app.mail_sender = "admin.example@vikuit.com"
			app.mail_footer = ""
			app.max_results = 20
			app.max_results_sublist = 20
			import sha, random
			app.session_seed = sha.new(str(random.random())).hexdigest()
			app.version = UPDATER_VERSION
			app.put()
			
			user = model.UserData(nickname='admin',
				email='admin.example@vikuit.com',
				password='1:c07cbf8821d47575a471c1606a56b79e5f6e6a68',
				language='en',
				articles=0,
				draft_articles=0,
				messages=0,
				draft_messages=0,
				comments=0,
				rating_count=0,
				rating_total=0,
				rating_average=0,
				threads=0,
				responses=0,
				communities=0,
				favourites=0,
				public=False,
				contacts=0,
				rol='admin')
			user.put()
			
			parent_category = model.Category(title='General',
			   description='General category description',
			   articles = 0,
			   communities = 0)
			parent_category.put()
			
			category = model.Category(title='News',
			   description='News description',
			   articles = 0,
			   communities = 0)
			
			category.parent_category = parent_category
			category.put()
			
			post = model.Mblog(author=user,
			author_nickname=user.nickname,
			content='Welcome to Vikuit!!',
			responses=0)
			post.put()
		
# update from 0.7 to 0.8 release	
def update07to08():
		
		app = model.Application.all().get()
		app.theme = 'blackbook'
		app.version = '0.8'
		app.put()
		memcache.delete('app')
		AppProperties().updateJinjaEnv()
		return
		
	# update from 0.8 to 0.9 release	
def update08to09():
		
		app = model.Application.all().get()
		app.version = '0.9'
		app.put()

	# update from 0.9 to 01 release	
def update09to10():
		
		app = model.Application.all().get()
		app.version = '1.0'
		app.put()
		