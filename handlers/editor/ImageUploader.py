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
import datetime
import os
import model
import logging

from google.appengine.api import memcache
from google.appengine.ext import webapp
from handlers.AuthenticatedHandler import AuthenticatedHandler

class ImageUploader(AuthenticatedHandler):
    
    def execute(self):
        method = self.request.method
        user = self.values['user']
                
        if method == 'GET':#Request identifies actions
            action = self.get_param('act')
            url_path = self.get_param('url')
            query = model.Image.gql('WHERE url_path=:1', url_path )
            image = query.get()
                        
            if not image:
                self.render_json({ 'saved': False, 'msg': self.getLocale('Not found') })
            elif user.nickname != image.author_nickname and user.rol != 'admin':
                self.render_json({ 'saved': False, 'msg': self.getLocale('Not allowed') })
            elif action == 'del': #delete image
                image.delete()
                self.render_json({ 'saved': True })
            else:
                self.render_json({ 'saved': False }) 
                       
        else:#File upload
            # Get the uploaded file from request.
            upload = self.request.get("upload")
            
            nick = user.nickname
            dt = datetime.datetime.now()
            prnt = dt.strftime("%Y%m%d%H%M%S")
            url_path = nick +"/"+ prnt
            
            try: 
                query = model.Image.all(keys_only=True).filter('url_path', url_path)
                entity = query.get()
                if entity:
                    raise Exception('unique_property must have a unique value!')
                
                image = model.Image(author=user,
                                    author_nickname=nick,
                                    thumbnail=upload,
                                    url_path=url_path)
                
                image.put()
                self.values["label"] = self.getLocale("Uploaded as: %s") % url_path
            except:
                self.values["label"] = self.getLocale('Error saving image')
            
            self.render("/translator-util.html")
            
        return 