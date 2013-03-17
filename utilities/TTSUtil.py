#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# (C) Copyright 2011 John Cube <jonh.cube[a]vikuit.com>
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

from google.appengine.api import urlfetch
from utilities.BeautifulSoup import *
import urllib
import sys

class TTSUtil (object):
    __instance = None
    __appDic = None
    __env = None

    def get_tts_stream_from_tts_urs(self,tts_urls):
        
        content=""
        for tts_url in tts_urls:
            url = "http://translate.google.com/translate_tts?tl=es&q=" + tts_url
        
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'    
            
            try:
                result = urlfetch.fetch(url,
                                payload=' ',
                                method=urlfetch.GET,
                                headers={'Content-Type': 'text/xml;charset=UTF-8', 'User-Agent' : user_agent})
         
                if result.status_code == 200:
                    content=content+result.content
            except:
                sys.__stdout__.write("Unexpected error:"+ str(sys.exc_info()[0]))
        #return the content
        return content
    
    def get_tts_url_from_html(self,html=None):
        
        # Constants (moove up)
        TTS_MAX_CHARACTERS=130
        # TTS mp3 urls
        tts_urls=[];
        # convert HTML to parsed text
        hexentityMassage = [(re.compile('&#x([^;]+);'), lambda m: '&#%d;' % int(m.group(1), 16))]
        soup=BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES,markupMassage=hexentityMassage)
        # remove all tags
        text=''.join(soup.findAll(text=True))
        # remove %0A characters
        tokens=text.strip('%0A').split('.')
        
        # iterate over the tokens (base on dot)    
        for token in tokens:      
            commatokens=token.split(',')
            # iterate over the tokens (base on comma)    
            for commatoken in commatokens:
                # encode as url params
                params=urllib.quote(commatoken.encode('utf-8'),'')
                previous_index=0
                while (previous_index<len(params)):
                    last_index=params.rfind('%20',previous_index,previous_index+TTS_MAX_CHARACTERS)
                    if (len(params)-previous_index)<=TTS_MAX_CHARACTERS: last_index=len(params)
                    tts_urls.append(params[previous_index:last_index])    
                    previous_index=last_index
            
        return tts_urls    
