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
import re
import model
import datetime

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from utilities import Constant
from utilities.AppProperties import AppProperties

class BaseHandler(webapp.RequestHandler):
	

	#########################
	### Handler functions ###
	#########################
	def get(self):
				
		if self.request.url.split('/')[2] == AppProperties().getAppDic().get(Constant.domain):#'vikuit.com':
			self.redirect(self.get_application().url + self.request.url.split('/', 3)[3], permanent=True)# 'http://www.vikuit.com/'
			return
		
		try:
			self.common_stuff()
			self.pre_execute()
		except CapabilityDisabledError:
			self.values = {}
			self.render('templates/maintenace.html')
			return
	
	
	def post(self):
		self.common_stuff()
		self.pre_execute()


	def pre_execute(self):
		self.execute()
	
	
	def common_stuff(self):
		self.values = {}
		self.user = None
		
		import session
		#app = model.Application.all().get()
		app = self.get_application()
		if app:
			self.sess = session.Session(app.session_seed)
			if self.sess.load():
				self.user = self.get_current_user()
			elif self.is_google_account():
				#google account users.get_current_user()
				#user only arrives here 1 time per session
				self.user = self.get_current_user()
				if self.user:
					redirect, self.user = self.store_google_account()
					self.sess.store(str(self.user.key()), 7200)
					if redirect:
						# redirect to preferences page
						self.redirect("/module/user.edit")
					if self.user.banned_date is not None:
						msg = self.getLocale("User '%s' was blocked. Contact with an administrator.") % self.user.nickname()
						self.show_error( msg )

		else:
			self.sess = None
			
		redirect = '%s?%s' % (self.request.path, self.request.query)
		self.values['sess'] = self.sess
		self.values['redirect'] = redirect
		self.values['app'] = self.get_application()
		self.values['activity_communities'] = self.communities_by_activity()

		if self.user:
			self.values['auth'] = self.sess.auth
			self.values['logout'] = '/module/user.logout?redirect_to=%s&auth=%s' % (self.quote(redirect), self.sess.auth)
			"""
			user_data = model.UserData.gql('WHERE email=:1', user.email()).get()
			if not user_data:
				user_data = model.UserData(email=user.email(),
					nickname=user.nickname(),
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
					public=False)
				user_data.put()
			self.values['user'] = user_data
			"""
			# TODO deprecated, use self.user instead
			self.values['user'] = self.user
		else:
			self.user = None
			self.values['user'] = None
			self.values['login'] = '/module/user.login?redirect_to=%s' % self.quote(redirect) # users.create_login_url(self.values['redirect'])
			self.values['glogin'] = users.create_login_url(self.values['redirect'])

	#################################################
	### Authentication and Autorization functions ###
	#################################################	
	def hash(self, login, p, times=100):
		import sha
		p = p.encode('ascii', 'ignore')
		p = '%s:%s' % (login, p)
		for i in range(0, times):
			p = sha.new(p).hexdigest()
		return p
	
	
	def can_write(self, community):
		if community.all_users is None or community.all_users:
			return True
		user = self.values['user']
		if not user:
			return False
		if model.CommunityUser.all().filter('community', community).filter('user', user).get():
			return True
		return False
	
	
	def check_password(self, user, password):
		times = 100
		user_password = user.password
		s = user.password.split(':')
		if len(s) > 1:
			times = int(s[0])
			user_password = s[1]

		return self.hash(user.nickname, password, times) == user_password
	
	
	def hash_password(self, nickname, password):
		times = 1
		return '%d:%s' % (times, self.hash(nickname, password, times))
	
	
	def auth(self):	
		token = self.values['auth']
		b = token == self.get_param('auth')
		if not b:
			self.forbidden()
		return b
	
	
	def get_current_user(self):
		if self.sess.user:##first
			return db.get(self.sess.user)
		user = users.get_current_user()#login with google account
#		if user: 
#			user = model.UserData.gql('WHERE email=:1', user.email()).get()
		return user

	

	def is_google_account(self):
		user = users.get_current_user()
		if user:
			return True
		else:
			return False
		
	def store_google_account(self):
		googleAcc = users.get_current_user()
		user = model.UserData.gql('WHERE email=:1', googleAcc.email()).get()
		redirectPreferences = False
		if user is None:
			redirectPreferences = True
			nick = self.getNickname(googleAcc.nickname())
			user = model.UserData(nickname=nick,
				email=googleAcc.email(),
				password=None,#Change to optional
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
				contacts=0)
			user.registrationType = 1 #Google identifier
		
		user.last_login = datetime.datetime.now()
		user.put()
		
		if redirectPreferences:
			# Is new user
			app = model.Application.all().get()
			if app:
				app.users += 1
				app.put()
			memcache.delete('app')
		return redirectPreferences, user
			
	def getNickname(self, nick, isMail=True):
		if isMail:
			return nick.split('@')[0]
		else:
			return nick


	###########################
	### Bussiness functions ###
	###########################
	def add_user_subscription(self, user, subscription_type, subscription_id):
		user_subscription = model.UserSubscription(user=user,
			user_nickname=user.nickname,
			user_email=user.email,
			subscription_type=subscription_type,
			subscription_id=subscription_id,
			creation_date = datetime.datetime.now())
		subscription = model.UserSubscription.all().filter('user', user).filter('subscription_type', subscription_type).filter('subscription_id', subscription_id).get()
		if subscription is None:
			user_subscription.put()
		
			
	def remove_user_subscription(self, user, subscription_type, subscription_id):
		user_subscription = model.UserSubscription.all().filter('user', user).filter('subscription_type', subscription_type).filter('subscription_id', subscription_id).get()
		if user_subscription is not None:
			user_subscription.delete()
			
			
	def add_follower(self, community=None, user=None, article=None, thread=None, nickname=None):
		object_type = None
		obj = None
		if user is not None:
			object_type = 'user'
			obj = user
		elif community is not None:
			object_type = 'community'
			obj = community
		elif thread is not None:
			object_type = 'thread'
			obj = thread
		elif article is not None:
			object_type = 'article'
			obj = article
		if object_type is None:
			return None
			
		follower = model.Follower.all().filter('object_type', object_type).filter('object_id', obj.key().id()).get()
		
		if follower:
			if nickname not in follower.followers:
				follower.followers.append(nickname)
				follower.put()
		else:
			follower = model.Follower(object_type=object_type,
				object_id=obj.key().id(),
				followers=[nickname])
			follower.put()
	
	
	def remove_follower(self, community=None, user=None, article=None, thread=None, nickname=None):
		object_type = None
		obj = None
		if user is not None:
			object_type = 'user'
			obj = user
		elif community is not None:
			object_type = 'community'
			obj = community
		elif thread is not None:
			object_type = 'thread'
			obj = thread
		elif article is not None:
			object_type = 'article'
			obj = article
		if object_type is None:
			return None
			
		follower = model.Follower.all().filter('object_type', object_type).filter('object_id', obj.key().id()).get()
		
		if follower:
			if nickname in follower.followers:
				follower.followers.remove(nickname)
				follower.put()
	
	
	def create_event(self, event_type, followers,
		user, user_to=None, community=None, article=None, thread=None, creation_date=None,
		response_number=0):
		event = model.Event(event_type=event_type,
			followers=followers,
			user=user,
			user_nickname=user.nickname,
			response_number=response_number)
		
		if user_to is not None:
			event.user_to = user_to
			event.user_to_nickname = user_to.nickname
		
		if community is not None:
			event.community = community
			event.community_title = community.title
			event.community_url_path = community.url_path
		
		if article is not None:
			event.article = article
			event.article_title = article.title
			event.article_author_nickname = article.author_nickname
			event.article_url_path = article.url_path
		
		if thread is not None:
			event.thread = thread
			event.thread_title = thread.title
			event.thread_url_path = thread.url_path
		
		if creation_date is None:
			event.creation_date = datetime.datetime.now()
		else:
			event.creation_date = creation_date
		
		event.put()
	
	
	def get_followers(self, user=None, community=None, thread=None, article=None):
		object_type = None
		obj = None
		if user is not None:
			object_type = 'user'
			obj = user
		elif community is not None:
			object_type = 'community'
			obj = community
		elif thread is not None:
			object_type = 'thread'
			obj = thread
		elif article is not None:
			object_type = 'article'
			obj = article
		if object_type is None:
			return None
		
		object_id = obj.key().id()
		follower = model.Follower.all().filter('object_type', object_type).filter('object_id', object_id).get()
		if not follower:
			follower = model.Follower(object_type=object_type, object_id=object_id, followers=[])
			follower.put()
		
		return follower.followers
	
	
	def create_task(self, task_type, priority, data):
		import simplejson
		t = model.Task(task_type=task_type, priority=priority, data=simplejson.dumps(data))
		t.put()


	def is_contact(self, this_user):
		user = self.values['user']
		if not user:
			return False
		if model.Contact.all().filter('user_from', user).filter('user_to', this_user).get():
			return True
		return False


	def create_community_subscribers(self, community):	
		if not community.subscribers:
			com = [g.user.email for g in model.CommunityUser.all().filter('community', community).fetch(1000) ]
			community.subscribers = list(set(com))


	# I use strings in order to distinguish three values into the templates
	# 'True', 'False', and None
	def joined(self, community):
		gu = model.CommunityUser.gql('WHERE community=:1 and user=:2', community, self.values['user']).get()
		if gu is not None:
			return 'True'
		return 'False'


	def communities_by_activity(self):
		key = 'activity_communities'
		g = memcache.get(key)
		if g is not None:
			return g
		else:
			communities = model.Community.all().order('-activity').fetch(15)
			memcache.add(key, communities, 3600)
			return communities

	
	def add_categories(self):
		cats = list(model.Category.all().order('title'))
		categories = {}
		for category in cats:
			# legacy code
			if not category.url_path:
				category.url_path = self.to_url_path(category.title)
				category.put()
			# end
			if category.parent_category is None:
				categories[str(category.key())] = category

		for category in cats:
			if category.parent_category is not None:
				parent_category = categories[str(category.parent_category.key())]
				if not parent_category.subcategories:
					parent_category.subcategories = []
				parent_category.subcategories.append(category)

		ret = [categories[key] for key in categories]
		ret.sort()
		self.values['categories'] = ret


	def add_tag_cloud(self):
		self.values['tag_cloud'] = self.cache('tag_cloud', self.get_tag_cloud)

	def get_tag_cloud(self):
		return self.tag_list(model.Tag.all().order('-count').fetch(30))
	
	def parse_tags(self, tag_string):
		tags = [self.to_url_path(t) for t in tag_string.split(',')]
		return list(set(tags))
	
	def delete_tags(self, tags):
		tags=set(tags)
		for tag in tags:
			t = model.Tag.gql('WHERE tag=:1', tag).get()
			if t:
				if t.count == 1:
					t.delete()
				else:
					t.count = t.count - 1
					t.put()
	
	def update_tags(self, tags):
		tags=set(tags)
		for tag in tags:
			t = model.Tag.gql('WHERE tag=:1', tag).get()
			if not t:
				tg = model.Tag(tag=tag,count=1)
				tg.put()
			else:
				t.count = t.count + 1
				t.put()
	
	def tag_list(self, tags):
		tagdict={}
		for t in tags:
			tagdict[t.tag] = t.count
		if not tagdict:
			return []
		maxcount = max(t.count for t in tags)
		taglist = [(tag, 6*tagdict[tag]/maxcount, tagdict[tag]) for tag in tagdict.keys()]
		taglist.sort()
		return taglist


	###############################
	### Evnironment And Renders ###
	###############################
	def create_jinja_environment(self):
		env = AppProperties().getJinjaEnv()
		env.filters['relativize'] = self.relativize
		env.filters['markdown'] = self.markdown
		env.filters['smiley'] = self.smiley
		env.filters['pagination'] = self.pagination
		env.filters['media'] = self.media_content
		env.filters['quote'] = self.quote
		return env
	
	def get_template(self, env, f):
		p = f.split('/')
		if p[0] == 'templates':
			f = '/'.join(p[1:])
		t = env.get_template(f)
		return t
	
	def render_chunk(self, f, params):
		env = self.create_jinja_environment()
		t = self.get_template(env, f)
		return t.render(params)

	def render(self, f):
		self.response.headers['Content-Type'] = 'text/html;charset=UTF-8'
		self.response.headers['Pragma'] = 'no-cache'
		self.response.headers['Cache-Control'] = 'no-cache'
		self.response.headers['Expires'] = 'Wed, 27 Aug 2008 18:00:00 GMT'
		self.response.out.write(self.render_chunk(f, self.values))

	
	def render_json(self, data):
		import simplejson
		self.response.headers['Content-Type'] = 'application/json;charset=UTF-8'
		self.response.headers['Pragma'] = 'no-cache'
		self.response.headers['Cache-Control'] = 'no-cache'
		self.response.headers['Expires'] = 'Wed, 27 Aug 2008 18:00:00 GMT'
		self.response.out.write(simplejson.dumps(data))

	def relativize(self, value):
		now = datetime.datetime.now()
		try:
			diff = now - value
		except TypeError:
			return ''
		days = diff.days
		seconds = diff.seconds
		if days > 365:
			return self.getLocale("%d years") % (days / 365, ) #u"%d años" % (days / 365, )
		if days > 30:
			return self.getLocale("%d months") % (days / 30, ) #u"%d meses" % (days / 30, )
		if days > 0:
			return self.getLocale("%d days") % (days, ) # u"%d días" % (days, )
		
		if seconds > 3600:
			return self.getLocale("%d hours") % (seconds / 3600, ) # u"%d horas" % (seconds / 3600, )
		if seconds > 60:
			return self.getLocale("%d minutes") % (seconds / 60, ) # u"%d minutos" % (seconds / 60, )
		
		return self.getLocale("%d seconds") % (seconds, ) # u"%d segundos" % (seconds, )
		
	def smiley(self, value):
		return value


	def markdown(self, value):
		try:
			import markdown
		except ImportError:
			return "error"
		else:
			return markdown.markdown(value, [], safe_mode='escape')
			
			
	def quote(self, value):
		import urllib
		value = self.get_unicode(value)
		return urllib.quote((value).encode('UTF-8'))
	
	
	def media_content(self,value):
		import MediaContentFilters as contents
		value=contents.media_content(value)
		return value

	###########################
	### Utilities functions ###
	###########################
	def mail(self, subject, body, to=[], bcc=[]):
		app = self.get_application()
		subject = "%s %s" % (app.mail_subject_prefix, subject)
		body = """
%s

%s
""" % (body,app.mail_footer)
		
		queue = model.MailQueue(subject=subject, body=body, to=to, bcc=bcc)
		queue.put()
			
			
	def show_error(self, message):
		self.values['message'] = message
		self.render('templates/error.html')
		
		
	"""
	def handle_exception(self, exception):
		self.response.clear()
		self.response.set_status(500)
		
		self.render('templates/error500.html')
	"""

	def not_found(self):
		self.response.clear()
		self.response.set_status(404)
		self.render('templates/error404.html')
		
		
	def forbidden(self):
		self.response.clear()
		self.response.set_status(403)
		self.render('templates/error403.html')
		

	def getLocale(self, label):
		return self.render_chunk("/translator-util.html", {"label": label})
	
	
	def get_application(self):
		return self.cache('app', self.fetch_application)
	
	
	def fetch_application(self):
		
		
		return model.Application.all().get()


	def value(self, key):
		try:
			return self.values[key]
		except KeyError:
			return None

	
	def not_none(self, value):
		if not value:
			return ''
		return value
	
	
	def get_param(self, key):
		return self.get_unicode(self.request.get(key))


	def get_unicode(self, value):
		try:
			value = unicode(value, "utf-8")
		except TypeError:
			return value
		return value
	
	
	def cache(self, key, function, timeout=0):
		# import logging
		# logging.debug('looking for %s in the cache' % key)
		data = memcache.get(key)
		if data is not None:
			# logging.debug('%s is already in the cache' % key)
			return data
		else:
			data = function.__call__()
			# logging.debug('inserting %s in the cache' % key)
			memcache.add(key, data, timeout)
			return data
	
	"""
	def cache_this(self, function, timeout=600):
		key = '%s?%s' % (self.request.path, self.request.query)
		return self.cache(key, function, timeout)
	
	def pre_pag(self, query, max, default_order=None):
		try:
			p = int(self.get_param('p'))
		except ValueError:
			p = 1
		offset = (p-1)*max
		o = self.get_param('o')
		if o:
			query = query.order(o)
			self.values['o'] = o
		elif default_order:
			query = query.order(default_order)
		return [obj for obj in query.fetch(max+1, offset)]
		
	def post_pag(self, a, max):
		try:
			p = int(self.get_param('p'))
		except ValueError:
			p = 1
		self.values['p'] = p
		if p > 1:
			self.values['prev'] = p-1
		l = len(a)
		if l > max:
			self.values['len'] = max
			self.values['next'] = p+1
			return a[:max]
		self.values['len'] = l
		o = self.get_param('o')
		if o:
			self.values['o'] = o
		return a
	"""

	def paging(self, query, max, default_order=None, total=-1, accepted_orderings=[], key=None, timeout=300):
		if total > 0:
			pages = total / max
			if total % max > 0:
				pages += 1
			self.values['pages'] = pages
		try:
			p = int(self.get_param('p'))
			if p < 1:
				p = 1
		except ValueError:
			p = 1
		self.values['p'] = p
		offset = (p-1)*max
		#if offset > 1000:
		#	return None
		o = self.get_param('o')
		if o and o in accepted_orderings:
			query = query.order(o)
			self.values['o'] = o
		elif default_order:
			query = query.order(default_order)
		# caching
		if not key is None:
			a = memcache.get(key)
			if a is None:
				a = [obj for obj in query.fetch(max+1, offset)]
				memcache.add(key, a, timeout)
		else:
			a = [obj for obj in query.fetch(max+1, offset)]
		#
		if p > 1:
			self.values['prev'] = p-1
		l = len(a)
		if l > max:
			self.values['len'] = max
			self.values['next'] = p+1
			return a[:max]
		self.values['len'] = l
		return a
	
	
	def pagination(self, value):
		prev = self.value('prev')
		next = self.value('next')

		s = ''
		if prev or next:
			params = []
			p = self.value('p')
			q = self.value('q')
			a = self.value('a')
			t = self.value('t')
			o = self.value('o')
			cat = self.value('cat')
			pages = self.value('pages')
			
			# order
			if cat:
				params.append('cat=%s' % cat)
   
			# query string
			if q:
				params.append('q=%s' % q)
   
			# type
			if t:
				params.append('t=%s' % t)
   
			# order
			if o:
				params.append('o=%s' % o)
   
			# anchor
			if a:
				a = '#%s' % str(a)
			else:
				a = ''

			common = '%s%s' % ('&amp;'.join(params), a)
			s = '<ul class="pagination">'
			if prev:
				if prev == 1:
					s = (u'%s <li class="previous"><a href="?%s">« ' % (s, common))+self.getLocale("Previous")+u'</a></li>'
				else:
					s = (u'%s <li class="previous"><a href="?p=%d&amp;%s">« ' % (s, prev, common))+self.getLocale("Previous")+u'</a></li>'
			else:
				s = (u'%s <li class="previous-off">« ' % s)+self.getLocale("Previous")+u'</li>'
			
			if pages:
				i = 1
				while i <= pages:
					if i == p:
						s = u'%s <li class="active">%d</li>' % (s, i)
					else:
						if i == 1:
							s = u'%s <li><a href="?%s">%d</a></li>' % (s, common, i)
						else:
							s = u'%s <li><a href="?p=%d&amp;%s">%d</a></li>' % (s, i, common, i)
					i += 1
			else:
				s = (u'%s <li class="active">' % s)+self.getLocale("Page")+u' %d </li>' % p
			if next:
				s = (u'%s <li class="next"><a href="?p=%d&amp;%s">' % (s, next, common))+self.getLocale("Next")+(u' »</a></li>')
			else:
				s = (u'%s <li class="next-off">' % s)+self.getLocale("Next")+u' »</li>'
			s = '%s</ul><br/><br/>' % s
		return s
	
	
	def to_url_path(self, value):
		value = value.lower()
		# table = maketrans(u'áéíóúÁÉÍÓÚñÑ', u'aeiouAEIOUnN')
		# value = value.translate(table)
		value = value.replace(u'á', 'a')
		value = value.replace(u'é', 'e')
		value = value.replace(u'í', 'i')
		value = value.replace(u'ó', 'o')
		value = value.replace(u'ú', 'u')
		value = value.replace(u'Á', 'A')
		value = value.replace(u'É', 'E')
		value = value.replace(u'Í', 'I')
		value = value.replace(u'Ó', 'O')
		value = value.replace(u'Ú', 'U')
		value = value.replace(u'ñ', 'n')
		value = value.replace(u'Ñ', 'N') # TODO improve + review URL path allowed chars 
		value = '-'.join(re.findall('[a-zA-Z0-9]+', value))
		return value
	
	
	def clean_ascii(self, value):
		# table = maketrans(u'áéíóúÁÉÍÓÚñÑ', u'aeiouAEIOUnN')
		# value = value.translate(table)
		value = value.replace(u'á', 'a')
		value = value.replace(u'é', 'e')
		value = value.replace(u'í', 'i')
		value = value.replace(u'ó', 'o')
		value = value.replace(u'ú', 'u')
		value = value.replace(u'Á', 'A')
		value = value.replace(u'É', 'E')
		value = value.replace(u'Í', 'I')
		value = value.replace(u'Ó', 'O')
		value = value.replace(u'Ú', 'U')
		value = value.replace(u'ñ', 'n')
		value = value.replace(u'Ñ', 'N') # TODO improve + review URL path allowed chars
		value = ' '.join(re.findall('[a-zA-Z0-9()_\.:;-]+', value))
		return value
	
	
	def unique_url_path(self, model, url_path):
		c = 1
		url_path_base = url_path
		while True:
			query = db.Query(model)
			query.filter('url_path =', url_path)
			count = query.count(1)
			if count > 0:
				url_path = '%s-%d' % (url_path_base, c)
				c = c + 1
				continue
			break
		return url_path