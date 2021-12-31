#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi, urllib, http.cookies, os
import cgitb; cgitb.enable()  # for troubleshooting
from ntumc_util import *
from ntumc_webkit import *
from lang_data_toolkit import *
from ntumc_tagdb import *

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)


##########################################################################
# CONSTANTS
##########################################################################
template_data = {
    'wnnam': wn_nam,
    'wnver': wnver,
    'wnurl': wnurl,
    'type': 'sequential',
    'taglcgi': taglcgi,
    'logincgi': logincgi,
    'title': 'NTU-MC Annotation Tool'

}
default_location = taglcgi # Default redirect location after login

##########################################################################
# Get fields from CGI
##########################################################################
form = cgi.FieldStorage()
##------------------------
version = form.getfirst("version", "0.1")
usrname_cgi = form.getvalue("usrname_cgi")
target = form.getvalue("target")
action = form.getvalue("action")

##########################################################################
# Get fields from Cookies
##########################################################################
# Look for the username cookie (if it can't find, it will use 'unknown' as default)
user_cookie = NTUMC_Cookies.read_user_cookie(usrname_cgi)
usrname = user_cookie['user_name'].value if user_cookie and 'user_name' in user_cookie else ''

##########################################################################
# Local variables
##########################################################################
logged_in = False # by default logged_in is False
cookie_text = None 

##########################################################################
# Utility functions
##########################################################################
#nothing here yet
 
##########################################################################
# Application logic code (process queries, access database, etc.)
##########################################################################
template_data['target'] = target if target else ''

# We can use usrname_cgi to override the value in cookie
if usrname_cgi and usrname_cgi in valid_usernames:
    usrname = usrname_cgi 
    cookie_text = http.cookies.SimpleCookie()
    cookie_text['user_name'] = usrname
    cookie_text['user_name']['expires'] = 6 * 60 * 60
    # we need to redirect to login again
    HTML.redirect('%s?target=%s' % (logincgi, target), cookie_text)

if usrname in valid_usernames:
    logged_in = True

template_data['logged_in'] = logged_in
# Process logout
if action == 'logout':
    cookie_text = http.cookies.SimpleCookie()
    cookie_text['user_name'] = ''
    cookie_text['user_name']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    HTML.redirect('login.cgi?target=%s' % (target,), cookie_text)

if logged_in:
    template_data['message'] = 'You have been logged in as %s, I\'m going to send you to %s.' % (usrname, target)
    if target:
        HTML.redirect(target)
    HTML.render_template('login.htm', template_data, cookie_text)
    #
else:
    template_data['message'] = 'Username doesn\'t exist or has been expired.'
    ##########################################################################
    # Render UI
    ##########################################################################
    HTML.render_template('login.htm', template_data, cookie_text)

