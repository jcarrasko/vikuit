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

from handlers.MainPage import *

### MODULES ###

# Admin
from handlers.module.admin.Admin import *
from handlers.module.admin.AdminCategories import *
from handlers.module.admin.AdminCategoryEdit import *
from handlers.module.admin.AdminApplication import *
from handlers.module.admin.CommunityAddRelated import *
from handlers.module.admin.AdminUsers import *
from handlers.module.admin.AdminModules import *
from handlers.module.admin.AdminLookAndFeel import *
from handlers.module.admin.AdminGoogle import *
from handlers.module.admin.AdminMail import *
from handlers.module.admin.AdminCache import *
from handlers.module.admin.AdminStats import *
# Articles
from handlers.module.article.ArticleList import *
from handlers.module.article.ArticleEdit import *
from handlers.module.article.ArticleView import *
from handlers.module.article.ArticleVote import *
from handlers.module.article.ArticleDelete import *
from handlers.module.article.ArticleComment import *
from handlers.module.article.ArticleFavourite import *
from handlers.module.article.ArticleCommentSubscribe import *
from handlers.module.article.ArticleCommentDelete import *
from handlers.module.article.ArticleAddCommunities import *
from handlers.module.article.ArticleCommentEdit import *
from handlers.module.article.ArticleVisit import *

# Communities
from handlers.module.community.CommunityList import *
from handlers.module.community.CommunityEdit import *
from handlers.module.community.CommunityView import *
from handlers.module.community.CommunityMove import *
from handlers.module.community.CommunityDelete import *
# community forums
from handlers.module.community.CommunityForumList import *
from handlers.module.community.CommunityForumEdit import *
from handlers.module.community.CommunityForumView import *
from handlers.module.community.CommunityForumReply import *
from handlers.module.community.CommunityForumSubscribe import *
from handlers.module.community.CommunityForumDelete import *
from handlers.module.community.CommunityThreadEdit import *
from handlers.module.community.CommunityForumMove import *
from handlers.module.community.CommunityForumVisit import *
# community articles
from handlers.module.community.CommunityArticleList import *
from handlers.module.community.CommunityNewArticle import *
from handlers.module.community.CommunityArticleDelete import *
# community users
from handlers.module.community.CommunityUserList import *
from handlers.module.community.CommunityUserUnjoin import *
from handlers.module.community.CommunityUserJoin import *

# Users
from handlers.module.user.UserList import *
from handlers.module.user.UserView import *
from handlers.module.user.UserEdit import *
from handlers.module.user.UserArticles import *
from handlers.module.user.UserLogin import *
from handlers.module.user.UserCommunities import *
from handlers.module.user.UserLogout import *
from handlers.module.user.UserRegister import *
from handlers.module.user.UserChangePassword import *
from handlers.module.user.UserForgotPassword import *
from handlers.module.user.UserResetPassword import *
from handlers.module.user.UserDrafts import *
from handlers.module.user.UserContact import *
from handlers.module.user.UserFavourites import *
from handlers.module.user.UserContacts import *
from handlers.module.user.UserPromote import *
from handlers.module.user.UserEvents import *
from handlers.module.user.UserForums import *

# Blogging
from handlers.module.mblog.MBlogEdit import * 

# Messages
from handlers.module.message.MessageEdit import *
from handlers.module.message.MessageSent import *
from handlers.module.message.MessageInbox import *
from handlers.module.message.MessageRead import *
from handlers.module.message.MessageDelete import *

### Common handlers / Other Handlers ###

# forums
from handlers.ForumList import *
#search
from handlers.SearchResult import *
# inviting contacts
from handlers.Invite import *
# feed RSS
from handlers.Feed import *
# images
from handlers.ImageDisplayer import *
from handlers.editor.ImageBrowser import *
from handlers.editor.ImageUploader import *

#Queue
from handlers.MailQueue import *
from handlers.TaskQueue import *

from handlers.Tag import *
from handlers.Search import *
from handlers.Dispatcher import *
from handlers.Initialization import *
from handlers.NotFound import *
from handlers.BaseRest import *
from handlers.Static import *
