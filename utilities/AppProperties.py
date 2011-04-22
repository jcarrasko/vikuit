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
import model
import PropertiesUtil
import Constant
from google.appengine.api import memcache

class AppProperties (object):
    __instance = None
    __appDic = None
    __env = None

    def __new__(cls, *args, **kargs): 
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kargs)      
        return cls.__instance
    
    '''
        Gets application properties
    '''
    def getAppDic(self):
        if self.__appDic is None:
            self.__appDic = PropertiesUtil.loadProperties(r"conf/application.properties")
        return self.__appDic

    '''
        Gets Jinja Environment
    '''
    def getJinjaEnv(self):
        import os
        import gettext
        from jinja2 import Template, Environment, FileSystemLoader
        if self.__env is None:
            self.__env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '..', 'templates' )), extensions=['jinja2.ext.i18n'])##MOD
            '''self.__env.filters['relativize'] = self.relativize
            self.__env.filters['markdown'] = self.markdown
            self.__env.filters['smiley'] = self.smiley
            self.__env.filters['pagination'] = self.pagination
            self.__env.filters['media'] = self.media_content
            self.__env.filters['quote'] = self.quote'''
            ######################################################################################
            # i18n configuration
            # Added: mo and po files
            # Mdofied: handlers and templates
            ######################################################################################
            locale = ''
            try :
                locale = self.get_application().locale
                if locale is None or locale == "" :
                    locale = Constant.DEFAULT_LOCALE
            except:
                locale = Constant.DEFAULT_LOCALE
            domain = 'django'
            localeDir = 'conf/locale'
            localeCodeset = 'UTF-8'
            langs=[locale]#, 'ca_ES', 'es']#'es', 
            #os.environ["LANGUAGE"] = "en"
            translations = gettext.translation(domain, localeDir, languages=langs) #GNUTranslations
            #env = Environment(extensions=['jinja2.ext.i18n'])
            self.__env.install_gettext_translations(translations)
            gettext.textdomain(domain)
            gettext.bindtextdomain(gettext._current_domain, localeDir)
            gettext.bind_textdomain_codeset(gettext._current_domain, localeCodeset)
            #self.__env.shared = True
        return self.__env
    
    def updateJinjaEnv(self):
        self.__env = None
        self.getJinjaEnv()
        
    def getAccountProvider(self, regType = 0):
    
        if regType is None or regType == 0:# Local
            return self.get_application().name
        elif regType == 1:
            return "Google"
        return ""
        
#Dup
    def get_application(self):
        
        app = memcache.get('app')
        if app is not None:
            # logging.debug('%s is already in the cache' % key)
            return app
        else:
            app = model.Application.all().get()
            # logging.debug('inserting %s in the cache' % key)
            memcache.add('app', app, 0)
            return app
