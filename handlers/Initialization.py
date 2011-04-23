#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Carrasco <jose.carrasco[a]vikuit.com>
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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from handlers.BaseHandler import *

class Initialization(BaseHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		
		app = model.Application.all().get()
		
		if app is None:
			populateDB()			
			self.response.out.write('App installed. Created user administrator. nickname="admin", password="1234". Please change the password.')
			return
		elif not app.session_seed:	
			import sha, random
			app.session_seed = sha.new(str(random.random())).hexdigest()
			app.put()
			self.response.out.write('Seed installed')
		
		return
		
		p = int(self.request.get('p'))
		key = self.request.get('key')
		action = self.request.get('action')
		if key:
			community = model.Community.get(key)
			if not community:
				self.response.out.write('community not found')
				return
		
		offset = (p-1)*10
		if action == 'gi':
			i = self.community_articles(community, offset)
		elif action == 'gu':
			i = self.community_users(community, offset)
		elif action == 'th':
			i = self.threads(offset)
		elif action == 'cc':
			i = self.contacts(offset)
		elif action == 'fv':
			i = self.favourites(offset)
		elif action == 'sg':
			i = self.show_communities(offset)
			return
		elif action == 'ut':
			i = self.update_threads(offset)
		elif action == 'uis':
			i = self.update_article_subscription(p-1)
			self.response.out.write('Processed from %d to %d. %d updated. Action %s' % (p-1, i[0], i[1], action))
			return
		elif action == 'ugs':
			i = self.update_community_subscription(community, offset)
		elif action == 'uts':
			i = self.update_thread_subscription(p-1)
			self.response.out.write('Processed from %d to %d. %d updated. Action %s' % (p-1, i[0], i[1], action))
			return
		elif action == 'ugc':
			i = self.update_community_counters(p-1)
			self.response.out.write('Processed from %d to %d. %d updated. Action %s' % (p-1, i[0], i[1], action))
			return
		elif action == 'adus':
			i = self.add_date_user_subscription(offset)
		elif action == 'afg':
			i = self.add_follower_community(offset)
		elif action == 'afu':
			i = self.add_follower_user(offset)
		elif action == 'afi':
			i = self.add_follower_article(offset)
		elif action == 'aft':
			i = self.add_follower_thread(offset)
		else:
			self.response.out.write('unknown action -%s-' % action)
			return
		self.response.out.write('Processed from %d to %d. %d updated. Action %s' % (offset, i[0], i[1], action))


	def community_articles(self, community, offset):
		i = offset
		p = 0
		for gi in model.CommunityArticle.all().filter('community', community).order('-creation_date').fetch(10, offset):
			if not gi.community_title:
				article = gi.article
				community = gi.community
				gi.article_author_nickname = article.author_nickname
				gi.article_title = article.title
				gi.article_url_path = article.url_path
				gi.community_title = community.title
				gi.community_url_path = community.url_path
				gi.put()
				p += 1
			i+=1
		return (i, p)

	def community_users(self, community, offset):
		i = offset
		p = 0
		for gu in model.CommunityUser.all().filter('community', community).order('-creation_date').fetch(10, offset):
			if not gu.community_title:
				user = gu.user
				community = gu.community
				gu.user_nickname = gu.user.nickname
				gu.community_title = community.title
				gu.community_url_path = community.url_path
				gu.put()
				p += 1
			i+=1
		return (i, p)

	def threads(self, offset):
		i = offset
		p = 0
		for th in model.Thread.all().order('-creation_date').fetch(10, offset):
			if not th.community_title:
				community = th.community
				th.community_title = community.title
				th.community_url_path = community.url_path
				if not th.url_path:
					th.url_path = th.parent_thread.url_path
				th.put()
				p += 1
			i+=1
		return (i, p)

	def contacts(self, offset):
		i = offset
		p = 0
		for cc in model.Contact.all().order('-creation_date').fetch(10, offset):
			if not cc.user_from_nickname:
				cc.user_from_nickname = cc.user_from.nickname
				cc.user_to_nickname = cc.user_to.nickname
				cc.put()
				p += 1
			i+=1
		return (i, p)

	def favourites(self, offset):
		i = offset
		p = 0
		for fv in model.Favourite.all().order('-creation_date').fetch(10, offset):
			if not fv.user_nickname:
				article = fv.article
				fv.article_author_nickname = article.author_nickname
				fv.article_title = article.title
				fv.article_url_path = article.url_path
				fv.user_nickname = fv.user.nickname
				fv.put()
				p += 1
			i+=1
		return (i, p)

	def show_communities(self, offset):
		for g in model.Community.all().order('-creation_date').fetch(10, offset):
			self.response.out.write("('%s', '%s', %d),\n" % (g.title, str(g.key()), g.members))
			
	def update_threads(self, offset):
		i = offset
		p = 0
		for th in model.Thread.all().filter('parent_thread', None).order('-creation_date').fetch(10, offset):
			if th.views is None:
				th.views = 0
				th.put()
				p += 1
			i+=1
		return (i, p)
		
	def update_article_subscription(self, offset):
		i = offset
		p = 0
		for article in model.Article.all().order('-creation_date').fetch(1, offset):
			if article.subscribers:
				for subscriber in article.subscribers:
					user = model.UserData.all().filter('email', subscriber).get()
					if not model.UserSubscription.all().filter('user', user).filter('subscription_type', 'article').filter('subscription_id', article.key().id()).get():
						self.add_user_subscription(user, 'article', article.key().id())
						p += 1
			i+=1
		return (i, p)
		
	def update_community_subscription(self, community, offset):
		i = offset
		p = 0
		for community_user in model.CommunityUser.all().filter('community', community).order('-creation_date').fetch(10, offset):
			if not model.UserSubscription.all().filter('user', community_user.user).filter('subscription_type', 'community').filter('subscription_id', community.key().id()).get():
				self.add_user_subscription(community_user.user, 'community', community.key().id())
				p += 1
			i += 1
		return (i, p)
			
	def update_thread_subscription(self, offset):
		i = offset
		p = 0
		for thread in model.Thread.all().filter('parent_thread', None).order('-creation_date').fetch(1, offset):
			if thread.subscribers:
				for subscriber in thread.subscribers:
					user = model.UserData.all().filter('email', subscriber).get()
					if not model.UserSubscription.all().filter('user', user).filter('subscription_type', 'thread').filter('subscription_id', thread.key().id()).get():
						self.add_user_subscription(user, 'thread', thread.key().id())
						p += 1
				i+=1
		return (i, p)
		
	def update_community_counters(self, offset):
		i = offset
		p = 0
		for community in model.Community.all().order('-creation_date').fetch(1, offset):
			users = model.CommunityUser.all().filter('community', community).count()
			articles = model.CommunityArticle.all().filter('community', community).count()
			community_threads = model.Thread.all().filter('community', community).filter('parent_thread', None)
			threads = community_threads.count()
			comments = 0
			for thread in community_threads:
				comments += model.Thread.all().filter('community', community).filter('parent_thread', thread).count()
			if community.members != users or community.articles != articles or community.threads != threads or community.responses != comments:
				community.members = users
				community.articles = articles
				community.threads = threads
				community.responses = comments
				p += 1
			if not community.activity:
				community.activity = 0
			community.activity = (community.members * 1) + (community.threads * 5) + (community.articles * 15) + (community.responses * 2)
			community.put()
			i += 1
		return (i, p)
			
	def add_date_user_subscription(self, offset):
		i = offset
		p = 0
		for user_subscription in model.UserSubscription.all().fetch(10, offset):
			if user_subscription.creation_date is None:
				user_subscription.creation_date = datetime.datetime.now()
				user_subscription.put()
				p += 1
			i += 1
		return (i, p)
		
	def add_follower_community(self, offset):
		i = offset
		p = 0
		for community_user in model.CommunityUser.all().fetch(10, offset):
			if community_user.user_nickname is None:
				self.desnormalizate_community_user(community_user)
			self.add_follower(community=community_user, nickname=community_user.user_nickname)
			p +=1
			i += 1
		return(i,p)
	
	def add_follower_user(self, offset):
		i = offset
		p = 0
		for cc in model.Contact.all().fetch(10, offset):
			if cc.user_from_nickname is None:
				self.desnormalizate_user_contact(cc)
			self.add_follower(user=cc.user_to, nickname=cc.user_from_nickname)
			p += 1
			i += 1
		return(i,p)
	
	def add_follower_article(self, offset):
		i = offset
		p = 0
		for article in model.Article.all().filter('deletion_date', None).filter('draft', False).fetch(10, offset):
			self.add_follower(article=article, nickname=article.author_nickname)
			p += 1
			i += 1
		return(i,p)
		
	def add_follower_thread(self, offset):
		i = offset
		p = 0
		for t in model.Thread.all().filter('parent_thread', None).fetch(10, offset):
			self.add_follower(thread=t, nickname=t.author_nickname)
			p += 1
			i += 1
		return(i, p)
		
	def desnormalizate_community_user(self, gu):
		user = gu.user
		community = gu.community
		gu.user_nickname = gu.user.nickname
		gu.community_title = community.title
		gu.community_url_path = community.url_path
		gu.put()
		
	def desnormalizate_user_contact(self, cc):
		cc.user_from_nickname = cc.user_from.nickname
		cc.user_to_nickname = cc.user_to.nickname
		cc.put()

def populateDB():
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
	