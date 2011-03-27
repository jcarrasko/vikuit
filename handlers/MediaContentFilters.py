#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (C) Copyright 2008 Juan Luis Belmonte <jlbelmonte at gmail dot com>
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

import re
#main method to apply all filters

def media_content(value):
    	if re.search('youtube',value):
        	value=youtube(value)
    	if re.search('vimeo', value):
        	value=vimeo(value)
#   	if re.search('slideshare', value):
#        	value=slideshare(value)
    	if re.search('veoh', value):
        	value=veoh(value)    
    	if re.search('metacafe', value):
        	value=metacafe(value)
        if re.search('video\.yahoo', value):
		value=yahoovideo(value)
#	if re.search('show\.zoho', value):
#		value=sohoshow(value)
#	if re.search('teachertube', value):
#		value=teachertube(value)
	return value

# specific methods for the different services

def youtube(text):
	targets = re.findall('media=http://\S+.youtube.com/watch\?v=\S+;', text)
    	for i in targets:
        	match= re.match('(.*)watch\?v=(\S+);',i)
        	html = '<p><object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/%s"&hl=en&fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%s"=es&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object></p>' % ( match.community(2), match.community(2))
        	text=text.replace(i,html)
    	return text

def vimeo(text):
    	targets = re.findall('media=\S*vimeo.com/\S+;',text)
    	for i in targets:
        	match = re.match('(\S*)vimeo.com/(\S+)',i)
        	html='<p><object width="400" height="300"><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=%s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1" /><embed src="http://vimeo.com/moogaloop.swf?clip_id=%s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="400" height="300"></embed></object></p>' % ( match.community(2), match.community(2))
        	text=text.replace(i,html)
    	return text

def slideshare(text):
    	targets = re.findall('(media=\[.*\];)', text)    
    	for i in targets:
		match = re.search('id=(.*)&doc=(.*)&w=(.*)',i)
		html = '<p><div style="width:425px;text-align:left" id="__ss_%s"><object style="margin:0px" width="%s" height="355"><param name="movie" value="http://static.slideshare.net/swf/ssplayer2.swf?doc=%s"/><param name="allowFullScreen" value="true"/><param name="allowScriptAccess" value="always"/><embed src="http://static.slideshare.net/swf/ssplayer2.swf?doc=%s" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%s" height="355"/></object></div></p>' %(match.community(1),match.community(3),match.community(2),match.community(2),match.community(3))
		text=text.replace(i,html)
    	return  text

def metacafe(text):
	targets = re.findall('media=\S+/watch/\d+/\S+/;', text)
	for i in targets:
		match = re.search('http://www.metacafe.com/watch/(\d+)/(\S+)/', i)
		html = '<p><embed src="http://www.metacafe.com/fplayer/%s/%s.swf" width="400" height="345" wmode="transparent" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash"> </embed></p>' %(match.community(1), match.community(2))
		text=text.replace(i,html)
	return text

def veoh(text):
	targets = re.findall('media=\S+veoh.com/videos/\S+;', text)
	for i in targets:
		match = re.search('http://www.veoh.com/videos/(\S+);',i)
		html = '<p><embed src="http://www.veoh.com/veohplayer.swf?permalinkId=%s&id=anonymous&player=videodetailsembedded&videoAutoPlay=0" allowFullScreen="true" width="410" height="341" bgcolor="#FFFFFF" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed></p>' % match.community(1)
		text = text.replace(i, html)
	return text

def yahoovideo(text):
	targets = re.findall('media=\S+video.yahoo.com/\S+/\d+\S+\d+;', text)
	for i in targets:
		match = re.search('video.yahoo.com/\S+/(\d+)/(\d+);', i)
		html='<p><div><object width="512" height="322"><param name="movie" value="http://d.yimg.com/static.video.yahoo.com/yep/YV_YEP.swf?ver=2.2.30" /><param name="allowFullScreen" value="true" /><param name="AllowScriptAccess" VALUE="always" /><param name="bgcolor" value="#000000" /><param name="flashVars" value="id=%s&vid=%s&lang=en-us&intl=us&embed=1" /><embed src="http://d.yimg.com/static.video.yahoo.com/yep/YV_YEP.swf?ver=2.2.30" type="application/x-shockwave-flash" width="512" height="322" allowFullScreen="true" AllowScriptAccess="always" bgcolor="#000000" flashVars="id=%s&vid=%s&lang=en-us&intl=us&embed=1" ></embed></object></div></p>' % (match.community(2),match.community(1),match.community(2),match.community(2))
		text = text.replace(i, html)

	return text

def teachertube(text):
	targets = re.findall('media=\S+/view_video.php\?viewkey=\S+;', text)
	for i in targets:
		match = re.search('viewkey=(\S+)',i)
		url_atom='%3'
		html='<embed src="http://www.teachertube.com/skin-p/mediaplayer.swf" width="425" height="350" type="application/x-shockwave-flash" allowfullscreen="true" menu="false" flashvars="height=350&width=425&file=http://www.teachertube.com/flvideo/64252.flv&location=http://www.teachertube.com/skin-p/mediaplayer.swf&logo=http://www.teachertube.com/images/greylogo.swf&searchlink=http://teachertube.com/search_result.php%sFsearch_id%sD&frontcolor=0xffffff&backcolor=0x000000&lightcolor=0xFF0000&screencolor=0xffffff&autostart=false&volume=80&overstretch=fit&link=http://www.teachertube.com/view_video.php?viewkey=%s&linkfromdisplay=true></embed>' % (url_atom, url_atom, match.community(1))
		text = text.replace(i, text)
	return text

def sohoshow(text):
	targets = re.findall('media=\S+show.zoho.com/public/\S+;', text)
	for i in targets:
		
		match = re.search('show.zoho.com/public/(\S+)/(\S+);',i)
		html='<p><embed height="335" width="450" name="Welcome3" style="border:1px solid #AABBCC" scrolling="no" src="http://show.zoho.com/embed?USER=%s&DOC=%s&IFRAME=yes" frameBorder="0"></embed></p>' % (match.community(1), match.community(2))
		text = text.replace(i, text)
	return text 

def dummy(text):
	return text

### skeleton
#def teacherstube(text):
#	targets = re.findall('', text)
#	for i in targets:
#		match = re.search('',text)
#		html=
#		text = text.replace(i, text)
#	return text



