#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 Jose Blanco <jose.blanco[a]vikuit.com>
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
from google.appengine.api import users
from google.appengine.ext import search
	
class UserData(search.SearchableModel):
	nickname = db.StringProperty(required=True)
	personal_message = db.StringProperty()
	email = db.StringProperty(required=True)
	avatar = db.BlobProperty()
	thumbnail = db.BlobProperty()
	image_version = db.IntegerProperty()
	list_urls = db.StringListProperty()
	im_addresses = db.StringListProperty()
	about_user = db.TextProperty()
	
	password = db.StringProperty(required=False)#mod to accept Google account
	registrationType = db.IntegerProperty()#0 -local, 1 - google
	rol = db.StringProperty()
	google_adsense = db.StringProperty()
	google_adsense_channel = db.StringProperty()
	token = db.StringProperty()
	checked = db.BooleanProperty()
	
	# articles
	articles = db.IntegerProperty(required=True)
	draft_articles = db.IntegerProperty(required=True)
	# messages
	messages = db.IntegerProperty(required=True)
	draft_messages = db.IntegerProperty(required=True)
	unread_messages = db.IntegerProperty()
	sent_messages = db.IntegerProperty()
	# comments
	comments = db.IntegerProperty(required=True)
	# rating
	rating_count = db.IntegerProperty(required=True)
	rating_total = db.IntegerProperty(required=True)
	rating_average = db.IntegerProperty(required=True)
	# forums
	threads = db.IntegerProperty(required=True)
	responses = db.IntegerProperty(required=True)
	# communities
	communities = db.IntegerProperty(required=True)
	# favourites
	favourites = db.IntegerProperty(required=True)
	# others
	real_name = db.StringProperty()
	country = db.StringProperty()
	city = db.StringProperty()
	public = db.BooleanProperty(required=True)
	contacts = db.IntegerProperty()

	last_update = db.DateTimeProperty(auto_now=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	last_login = db.DateTimeProperty()
	banned_date = db.DateTimeProperty()
	
	not_full_rss = db.BooleanProperty()

class ArticleHtml(db.Model):
	content = db.TextProperty(required=True)

class Article(search.SearchableModel):
	author = db.ReferenceProperty(UserData,required=True)
	author_nickname = db.StringProperty()
	title = db.StringProperty(required=True)
	description = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	content_html = db.ReferenceProperty(ArticleHtml)
	lic = db.StringProperty(required=True)
	views = db.IntegerProperty(required=True)
	rating_count = db.IntegerProperty(required=True)
	rating_total = db.IntegerProperty(required=True)
	rating_average = db.IntegerProperty()
	url_path = db.StringProperty(required=True)
	responses = db.IntegerProperty(required=True)
	tags = db.StringListProperty()
	favourites = db.IntegerProperty(required=True)
	
	draft = db.BooleanProperty(required=True)
	article_type = db.StringProperty(required=True)
	subscribers = db.StringListProperty()
	
	last_update = db.DateTimeProperty(auto_now=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	deletion_message = db.StringProperty()
	deletion_user = db.ReferenceProperty(UserData,collection_name='du')

class Mblog(search.SearchableModel):
	author = db.ReferenceProperty(UserData,required=True)
	author_nickname = db.StringProperty()
	content = db.TextProperty(required=True)
	responses = db.IntegerProperty(required=True)

	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	deletion_user_nick = db.StringProperty()

class Module(db.Model):
	name = db.TextProperty(required=True)
	active = db.BooleanProperty()

class Comment(db.Model):
	content = db.TextProperty(required=True)
	article = db.ReferenceProperty(Article,required=True)
	author = db.ReferenceProperty(UserData,required=True)
	author_nickname = db.StringProperty()
	response_number = db.IntegerProperty()
	
	last_update = db.DateTimeProperty(auto_now=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	editions = db.IntegerProperty()
	last_edition = db.DateTimeProperty()

class Vote(db.Model):
	user = db.ReferenceProperty(UserData,required=True)
	article = db.ReferenceProperty(Article,required=True)
	rating = db.IntegerProperty(required=True)

class Tag(db.Model):
	tag = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True)
	
class Category(db.Model):
	parent_category = db.SelfReferenceProperty()
	title = db.StringProperty(required=True)
	url_path = db.StringProperty()
	description = db.StringProperty(required=True)
	communities = db.IntegerProperty(required=True)
	articles = db.IntegerProperty(required=True)
	
	subcategories = None

class Community(search.SearchableModel):
	owner = db.ReferenceProperty(UserData,required=True)
	owner_nickname = db.StringProperty()
	title = db.StringProperty(required=True)
	description = db.StringProperty(required=True, multiline=True)
	url_path = db.StringProperty(required=True)
	old_url_path = db.StringProperty()
	subscribers = db.StringListProperty()
	
	members = db.IntegerProperty(required=True)
	articles = db.IntegerProperty(required=True)
	threads = db.IntegerProperty(required=True)
	responses = db.IntegerProperty(required=True)

	last_update = db.DateTimeProperty(auto_now=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	
	avatar = db.BlobProperty()
	thumbnail = db.BlobProperty()
	image_version = db.IntegerProperty()
	
	all_users = db.BooleanProperty()
	
	category = db.ReferenceProperty(Category, collection_name='communities_set')
	
	activity = db.IntegerProperty()

class CommunityUser(db.Model):
	user = db.ReferenceProperty(UserData,required=True)
	community = db.ReferenceProperty(Community,required=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	# denormalizationzation
	user_nickname = db.StringProperty()
	community_title = db.StringProperty()
	community_url_path = db.StringProperty()

class CommunityArticle(db.Model):
	article = db.ReferenceProperty(Article,required=True)
	community = db.ReferenceProperty(Community,required=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	# denormalization
	article_author_nickname = db.StringProperty()
	article_title = db.StringProperty()
	article_url_path = db.StringProperty()
	community_title = db.StringProperty()
	community_url_path = db.StringProperty()
	

class Thread(search.SearchableModel):
	community = db.ReferenceProperty(Community,required=True)
	community_title = db.StringProperty()
	community_url_path = db.StringProperty()
	author = db.ReferenceProperty(UserData,required=True)
	author_nickname = db.StringProperty()
	title = db.StringProperty(required=True)
	url_path = db.StringProperty()
	content = db.TextProperty(required=True)
	subscribers = db.StringListProperty()
	
	last_response_date = db.DateTimeProperty()
	response_number = db.IntegerProperty()
	
	editions = db.IntegerProperty()
	last_edition = db.DateTimeProperty()
	
	# responses
	parent_thread = db.SelfReferenceProperty()
	
	responses = db.IntegerProperty(required=True)
	latest_response = db.DateTimeProperty()

	last_update = db.DateTimeProperty(auto_now=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	deletion_date = db.DateTimeProperty()
	
	deletion_message = db.StringProperty()
	views = db.IntegerProperty()

class Favourite(db.Model):
	article = db.ReferenceProperty(Article,required=True)
	user = db.ReferenceProperty(UserData,required=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	# denormalize
	article_author_nickname = db.StringProperty()
	article_title = db.StringProperty()
	article_url_path = db.StringProperty()
	user_nickname = db.StringProperty()
	
class Contact(db.Model):
	user_from = db.ReferenceProperty(UserData,required=True,collection_name='cf')
	user_to = db.ReferenceProperty(UserData,required=True,collection_name='ct')
	creation_date = db.DateTimeProperty(auto_now_add=True)
	# denormalize
	user_from_nickname = db.StringProperty()
	user_to_nickname = db.StringProperty()

class Application(db.Model):
	
	name = db.StringProperty()
	logo = db.BlobProperty()
	theme = db.StringProperty()
	subject = db.StringProperty()
	locale = db.StringProperty()
	
	users = db.IntegerProperty()
	communities = db.IntegerProperty()
	articles = db.IntegerProperty()
	threads = db.IntegerProperty()
	
	url = db.StringProperty()
	
	mail_contact = db.StringProperty()
	mail_subject_prefix = db.StringProperty()
	mail_sender = db.StringProperty()
	mail_footer = db.StringProperty()
	
	recaptcha_public_key = db.StringProperty()
	recaptcha_private_key = db.StringProperty()
	
	google_adsense = db.StringProperty()
	google_adsense_channel = db.StringProperty()
	google_analytics = db.StringProperty()
	
	max_results = db.IntegerProperty()
	max_results_sublist = db.IntegerProperty()
	
	session_seed = db.StringProperty()
	
	version = db.StringProperty()
	
class Message(db.Model):
	user_from = db.ReferenceProperty(UserData,required=True,collection_name='mf')
	user_to = db.ReferenceProperty(UserData,required=True,collection_name='mt')
	creation_date = db.DateTimeProperty(auto_now_add=True)
	title = db.StringProperty(required=True)
	url_path = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	read = db.BooleanProperty(required=True)
	from_deletion_date = db.DateTimeProperty()
	to_deletion_date = db.DateTimeProperty()

	user_from_nickname = db.StringProperty()
	user_to_nickname = db.StringProperty()

class RelatedCommunity(db.Model):
	community_from = db.ReferenceProperty(Community,required=True,collection_name='gf')
	community_to = db.ReferenceProperty(Community,required=True,collection_name='gt')
	creation_date = db.DateTimeProperty(auto_now_add=True)
	# denormalization
	community_from_title = db.StringProperty(required=True)
	community_from_url_path = db.StringProperty(required=True)
	community_to_title = db.StringProperty(required=True)
	community_to_url_path = db.StringProperty(required=True)
	
class UserSubscription(db.Model):
	user = db.ReferenceProperty(UserData,required=True)
	user_email = db.StringProperty(required=True)
	user_nickname = db.StringProperty(required=True)
	subscription_type = db.StringProperty(required=True)
	subscription_id = db.IntegerProperty(required=True)
	creation_date = db.DateTimeProperty()
	
class Follower(db.Model):
	object_type = db.StringProperty(required=True)
	object_id = db.IntegerProperty(required=True)
	followers = db.StringListProperty()

class Event(db.Model):
	event_type = db.StringProperty(required=True)
	followers = db.StringListProperty()
	
	user = db.ReferenceProperty(UserData,required=True)
	user_nickname = db.StringProperty(required=True)
	
	user_to = db.ReferenceProperty(UserData,collection_name='events_user_to')
	user_to_nickname = db.StringProperty()
	
	community = db.ReferenceProperty(Community)
	community_title = db.StringProperty()
	community_url_path = db.StringProperty()
	
	article = db.ReferenceProperty(Article)
	article_author_nickname = db.StringProperty()
	article_title = db.StringProperty()
	article_url_path = db.StringProperty()
	
	thread = db.ReferenceProperty(Thread)
	thread_title = db.StringProperty()
	thread_url_path = db.StringProperty()
	
	response_number = db.IntegerProperty()
	
	creation_date = db.DateTimeProperty(auto_now_add=True)

class MailQueue(db.Model):
	subject = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	to = db.StringListProperty()
	bcc = db.StringListProperty()

class Recommendation(db.Model):
	article_from = db.ReferenceProperty(Article,collection_name='recommendations_from')
	article_to = db.ReferenceProperty(Article,collection_name='recommendations_to')
	value = db.FloatProperty()
	
	article_from_title = db.StringProperty(required=True)
	article_to_title = db.StringProperty(required=True)
	
	article_from_author_nickname = db.StringProperty(required=True)
	article_to_author_nickname = db.StringProperty(required=True)
	
	article_from_url_path = db.StringProperty(required=True)
	article_to_url_path = db.StringProperty(required=True)

class Task(db.Model):
	task_type = db.StringProperty(required=True)
	priority = db.IntegerProperty(required=True)
	data = db.StringProperty(required=True, multiline=True)
	creation_date = db.DateTimeProperty(auto_now_add=True)
	
class Image(db.Model):
	# No restrictions by community or user
	# All files are public, but only owner or admin can browse them
	# Due image size, those must be deleted.
	author = db.ReferenceProperty(UserData,required=True)
	author_nickname = db.StringProperty(required=True)

	thumbnail = db.BlobProperty(required=True)
	url_path = db.StringProperty(required=True)#Unique
	image_version = db.IntegerProperty()

	creation_date = db.DateTimeProperty(auto_now_add=True)
