#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# (C) Copyright 2008 Néstor Salceda <nestor.salceda at gmail dot com>
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

from google.appengine.api import mail
from google.appengine.runtime import apiproxy_errors

from google.appengine.ext import webapp

class MailQueue(webapp.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		n = 10
		
		next = model.MailQueue.all().get()
		sent = None	
		if not next:
			self.response.out.write('No pending mail')
			return
		if not next.bcc and not next.to:
			self.response.out.write('email without recipients')
			next.delete()
			return
				
		if next.bcc:
			bcc = next.bcc[:n]
			del next.bcc[:n]
			sent = self.send_mail(next, bcc=bcc)
		elif next.to:
			to = next.to[:n]
			del next.to[:n]
			sent = self.send_mail(next, to=to)
		
		if not sent:
			self.response.out.write('error. Mail was not sent')
			return
		
		if next.bcc or next.to:
			next.put()
			self.response.out.write('mail sent, something pending')
		else:
			next.delete()
			self.response.out.write('mail sent, mail queue deleted')
		
	def send_mail(self, queue, bcc=[], to=[]):
		app = model.Application.all().get()
		message = mail.EmailMessage(sender=app.mail_sender,
					subject=queue.subject, body=queue.body)
		
		if not to:
			to = app.mail_sender
		message.to = to
		if bcc:
			message.bcc = bcc
			
		try:
			message.send()
		except apiproxy_errors.OverQuotaError, message:
			return False
		return True
		
		
