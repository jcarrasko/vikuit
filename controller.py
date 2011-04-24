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

import wsgiref.handlers

from handlers import *
from handlers import Updater
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

# webapp.template.register_template_library('django.contrib.markup.templatetags.markup')
webapp.template.register_template_library('templatefilters')

def main():
	
	
	Updater.update()

	application = webapp.WSGIApplication(
									   [('/', MainPage),
									   # Module articles
									   ('/module/article.list',				ArticleList),
									   ('/module/article.edit',				ArticleEdit),
									   ('/module/article.favourite',		ArticleFavourite),
									   ('/module/article.vote',				ArticleVote),
									   ('/module/article/.*',				ArticleView),
									   ('/module/article.comment.subscribe',ArticleCommentSubscribe),
									   ('/module/article.comment',			ArticleComment),
									   ('/module/article.delete',			ArticleDelete),
									   ('/module/article.comment.delete',	ArticleCommentDelete),
									   ('/module/article.add.communities',		ArticleAddCommunities),
									   ('/module/article.comment.edit',		ArticleCommentEdit),
									   ('/module/article.visit',			ArticleVisit),
									   # Module users
									   ('/module/user.list',			UserList),
									   ('/module/user/.*',				UserView),
									   ('/module/user.edit',			UserEdit),
									   ('/module/user.register',		UserRegister),
									   ('/module/user.login',			UserLogin),
									   ('/module/user.logout',			UserLogout),
									   ('/module/user.changepassword',	UserChangePassword),
									   ('/module/user.forgotpassword',	UserForgotPassword),
									   ('/module/user.resetpassword',	UserResetPassword),
									   ('/module/user.drafts',			UserDrafts),
									   ('/module/user.articles/.*',		UserArticles),
									   ('/module/user.communities/.*',		UserCommunities),
									   ('/module/user.favourites/.*',	UserFavourites),
									   ('/module/user.contacts/.*',		UserContacts),
									   ('/module/user.contact',			UserContact),
									   ('/module/user.promote',			UserPromote),
									   ('/module/user.events',			UserEvents),
									   ('/module/user.forums/.*',		UserForums),
									   # Module Community
									   ('/module/community.list',			CommunityList),
									   ('/module/community.edit',			CommunityEdit),
									   ('/module/community.move',			CommunityMove),
									   ('/module/community.delete',			CommunityDelete),
									   ('/module/community/.*',				CommunityView),
									   ('/module/community.add.related',	CommunityAddRelated),
									   # Community forums
									   ('/module/community.forum.list/.*',	CommunityForumList),
									   ('/module/community.forum.edit',		CommunityForumEdit),
									   ('/module/community.forum/.*',		CommunityForumView),
									   ('/module/community.forum.reply',	CommunityForumReply),
									   ('/module/community.forum.subscribe',CommunityForumSubscribe),
									   ('/module/community.forum.delete',	CommunityForumDelete),
									   ('/module/community.thread.edit',	CommunityThreadEdit),
									   ('/module/community.forum.move',		CommunityForumMove),
									   ('/module/community.forum.visit',	CommunityForumVisit),
									   # Community articles
									   ('/module/community.article.list/.*',CommunityArticleList),
									   ('/module/community.article.add',	CommunityNewArticle),
									   ('/module/community.article.delete',	CommunityArticleDelete),
									   # Community users
									   ('/module/community.user.list/.*',	CommunityUserList),
									   ('/module/community.user.unjoin',	CommunityUserUnjoin),
									   ('/module/community.user.join',		CommunityUserJoin),
									   # messages
									   ('/message.edit',		MessageEdit),
									   ('/message.sent',		MessageSent),
									   ('/message.inbox',		MessageInbox),
									   ('/message.read/.*',		MessageRead),
									   ('/message.delete',		MessageDelete),
									   # forums,
									   ('/forum.list',			ForumList),
									   # inviting contacts
									   ('/invite',				Invite),
									   # rss
									   ('/feed/.*', 			Feed),
									   ('/module/mblog.edit', 	MBlogEdit),
									   ('/module/mblog/mblog.list', 	Dispatcher),
									   
									   ('/tag/.*', 				Tag),
									   ('/search', 				Search),
									   ('/search.result', 		SearchResult),
									   # images
									   ('/images/upload', 		ImageUploader),
									   ('/images/browse', 		ImageBrowser),
									   ('/images/.*', 			ImageDisplayer),
									   # module admin
									   ('/admin', 						Admin),
									   ('/module/admin.application',	AdminApplication),
									   ('/module/admin.categories',		AdminCategories),
									   ('/module/admin.category.edit',	AdminCategoryEdit),
									   ('/module/admin.users',			AdminUsers),
									   ('/module/admin.lookandfeel',	AdminLookAndFeel),
									   ('/module/admin.modules',		AdminModules),
									   ('/module/admin.mail',			AdminMail),
									   ('/module/admin.google',			AdminGoogle),
									   ('/module/admin.stats',			AdminStats),
                                       ('/module/admin.cache',          AdminCache),
									   # Ohters									   									   
									   ('/mail.queue',			MailQueue),
									   ('/task.queue',			TaskQueue),
									   #General
									   ('/about', 				Dispatcher),
									   #('/initialization', 		Initialization),
									   ('/html/.*', 			Static),
									   ('/.*', 					NotFound)],
									   debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
	main()
