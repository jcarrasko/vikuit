#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# (C) Copyright 2008 Alberto Gimeno <gimenete at gmail dot com>
# 
# This file is part of "debug_mode_on".
# 
# "debug_mode_on" is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# "debug_mode_on" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with "debug_mode_on".  If not, see <http://www.gnu.org/licenses/>.
# 

import model
import simplejson

from google.appengine.ext import webapp

class TaskQueue(webapp.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/plain;charset=utf-8'
		
		task = model.Task.all().order('-priority').get()
		
		if not task:
			self.response.out.write('No pending tasks')
			return
		
		data = simplejson.loads(task.data)
		data = self.__class__.__dict__[task.task_type].__call__(self, data)
		
		if data is None:
			self.response.out.write('Task finished %s %s' % (task.task_type, task.data))
			task.delete()
		else:
			task.data = simplejson.dumps(data)
			task.put()
			self.response.out.write('Task executed but not finished %s %s' % (task.task_type, task.data))
	
	def delete_recommendations(self, data):
		offset = data['offset']
		recs = model.Recommendation.all().fetch(1, offset)
		if len(recs) == 0:
			return None

		next = recs[0]

		article_to   = next.article_to
		article_from = next.article_from
		if article_from.draft or article_to.draft or article_from.deletion_date is not None or article_to.deletion_date is not None:
			next.delete()
		else:
			data['offset'] += 1

		return data
	
	def update_recommendations(self, data):
		offset = data['offset']
		recs = model.Recommendation.all().fetch(1, offset)
		if len(recs) == 0:
			return None

		next = recs[0]

		article_to   = next.article_to
		article_from = next.article_from
		
		self.calculate_recommendation(article_from, article_to)
		data['offset'] += 1

		return data
		
	def begin_recommendations(self, data):
		offset = data['offset']
		articles = model.Article.all().filter('draft', False).filter('deletion_date', None).order('creation_date').fetch(1, offset)
		print 'articles: %d' % len(articles)
		if len(articles) == 0:
			return None

		next = articles[0]
		data['offset'] += 1

		t = model.Task(task_type='article_recommendation', priority=0, data=simplejson.dumps({'article': next.key().id(), 'offset': 0}))
		t.put()

		return data
	
	def article_recommendation(self, data):
		article = model.Article.get_by_id(data['article'])
		if article.draft or article.deletion_date is not None:
			return None
		offset = data['offset']
		
		articles = model.Article.all().filter('draft', False).filter('deletion_date', None).order('creation_date').fetch(1, offset)
		if not articles:
			return None
		
		next = articles[0]
		data['offset'] += 1
		
		self.calculate_recommendation(next, article)
		
		return data
	
	def calculate_recommendation(self, next, article):
		def distance(v1, v2):
			all = []
			all.extend(v1)
			all.extend(v2)

			return float(len(all) - len(set(all)))
			
		def create_recommendation(article_from, article_to, value):
			return model.Recommendation(article_from=article_from,
				article_to=article_to,
				value=value,
				article_from_title=article_from.title,
				article_to_title=article_to.title,
				article_from_author_nickname=article_from.author_nickname,
				article_to_author_nickname=article_to.author_nickname,
				article_from_url_path=article_from.url_path,
				article_to_url_path=article_to.url_path)
		
		if next.key().id() == article.key().id():
			return
			
		r1 = model.Recommendation.all().filter('article_from', article).filter('article_to', next).get()
		r2 = model.Recommendation.all().filter('article_from', next).filter('article_to', article).get()
		diff = distance(article.tags, next.tags)
		if diff > 0:
			if not r1:
				r1 = create_recommendation(article, next, diff)
			else:
				r1.value = diff
				
			if not r2:
				r2 = create_recommendation(next, article, diff)
			else:
				r2.value = diff
				
			r1.put()
			r2.put()
		else:
			if r1:
				r1.delete()
			if r2:
				r2.delete()
