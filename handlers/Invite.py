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

from google.appengine.api import mail 
from google.appengine.ext import db
from handlers.BaseHandler import *
import re

class Invite(BaseHandler):
	
	def execute(self):
		user = self.values['user']
		method = self.request.method

		app = self.get_application()

		if not user:
			self.redirect('/module/user.login')
		
		if method == 'GET':
			#u"""Te invito a visitar %s, %s.\n %s
			self.values['personalmessage'] = self.getLocale("Let me invite you to visit %s, %s. %s")  % (app.name, app.subject, app.url) 
			self.render('templates/invite-friends.html')
			return
		elif self.auth():
			
			contacts = self.get_param('contacts').replace(' ','')
			contacts = contacts.rsplit(',',19)
			if contacts[0]=='' or not contacts:
				self.values['failed']=True
				self.render('templates/invite-friends.html')
				return
			self.values['_users'] = []
			
			
			invitations = []
			for contact in contacts:
				#FIXME inform the user about bad formed mails
				if re.match('\S+@\S+\.\S+', contact):
					u = model.UserData.gql('WHERE email=:1', contact).get()
					if u:
						self.values['_users'].append(u) 
					else:
						invitations.append(contact)
				
			personalmessage =  self.get_param('personalmessage')
			subject = self.getLocale("%s invites you to participate in %s") % (user.nickname, app.name)
			body = self.getLocale("Let me invite you to visit %s, %s. %s")  % (app.name, app.subject, app.url)
 
			if personalmessage:

				body = u"%s \n\n\n\n\t %s"  % (self.clean_ascii(personalmessage), self.get_application().url)
			self.mail(subject=subject, body=body, bcc=invitations)
	 		
			self.values['sent'] = True
			self.values['invitations'] = invitations
			self.render('templates/invite-friends.html')

