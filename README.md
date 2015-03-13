Vikuit wants to own every feature for a social network engine while remains easy to deploy and manage. Build over python and focused on the Google's Appengine, wants to fill the gap between SAAS platforms as Ning and on site deployments.

Between it's top key features, we can find:

Articles and news
Various languages support, such as english and spanish
Groups
Google native authentication
Microbloging
Follow a user
Profile and profile comments
Comments
Photo gallery
Full search
User dashboard
Recent activity
and new features that are coming soon, as chat o text-to-speech.

From the developer side, Vikuit uses themes (based on jinja templates) and special modules, called Vikuitlets, that give us a very easy way to extend it.
If you want to fast check the last features, come to http://demo.vikuit.com If you want to check our blog, come to http://blog.vikuit.com

Stay tuned ! on http://www.vikuit.com


##Getting Started
Getting started with Vikuit is very easy and don't takes more than five minutes !

Visit Vikuit's demo
If you want to see the features and how it works, without installing it, check our demo environment:

http://demo.vikuit.com

Install
Install Vikuit in your own GAE (Google's Appengine) is easy. Just must follow the next steps, and you will have an instance running.

1. Create your Google's Appengine Account and application
The first thing that you must have is a Google's Appengine Account. This account is free.

To sign in GAE, you can follow the next link:

https://appengine.google.com/

The next step is to create a new Application. Every application has its own identifier. This identifier is very important because is the name of your instance. Take note about it. Set the title, too.

2. Google's Appengine
The next step after you create your application, is to set up your Google's SDK. Google's SDK is an application that lets you to upload applications to the appengine (of course, it let you do more things...).

Do the follow:

Download and install Python 2.5.2. This is the version that runs on the Google App Engine and should therefore be used. http://www.python.org/download/releases/2.5.2/ From 1.0 we use Python 2.7. http://www.python.org/download/releases/2.7.3/
Download the Python version of the Google App Engine from Download Site for the GAE and install it.
3. Setting up Vikuit
The follow steps will prepare Vikuit to be deployed on Google's Appengine:

Download Vikuit package from http://www.vikuit.com/downloads
Extract it to one folder in your hardisk.
pj. C:\vikuit\

Inside the vikuit's folder, you will find one file called app.yaml
Modify the application value (first one) and set your application's identifier obtained when you create the application. Save it.
4. Deploy vikuit to your instance
For deploying Vikuit we will use the Google App Engine Launcher. This application was installed with the SDK. Launch the application and do the follow:

File >> Add Existing Application. Browse and select vikuit's folder on your computer.
Now, the launcher will show you your application with your specified identifier. Select it and click the deploy button up.
Set your email and password
Wait until the application tells that the deployment is finished ( one minute depending of your speed connection)
5. Test your instance
If you follow all the steps, now you will have your application installed on Google's Appengine.

The url of your's applications, will be:

http://your_identifier.appspot.com

For configuring your Vikuit instance:

Login. The default login / password for admin is:
user: admin password: 1234

Go to administration and check your values.
