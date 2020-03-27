#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Cookie, os, sys, codecs
from ntumc_util import *
from lang_data_toolkit import *

class HTML:

    @staticmethod
    def dropdownbox(name, values, selected=None):
        buf = []
        buf.append("<select name='%s'>" % name)
        for (value, text) in values:
            if value == selected:
                buf.append("<option value='%s' selected='true'>%s</option>" % (value, text))
            else:
                buf.append("<option value='%s'>%s</option>" % (value, text))
        buf.append("</select>")
        return u''.join(buf)

    # 2014-09-24 [Tuan Anh]
    # redirect to another web page
    @staticmethod
    def redirect(_target, _cookie_text=None):
        if not _target:
            _location = 'login'
        elif _target == 'taglex':
            _location = taglcgi
        elif _target == 'tagword':
            _location = tagwcgi
        elif _target == 'login':
            _location = logincgi
        else:
            _location = _target
        if _cookie_text:
            print(_cookie_text)
        jilog("I'm sending the user to %s" % _location)
        print("Location:%s\n\n" % _location)
        exit()


    #2014-09-16 [Tuan Anh] Add jinja2 support
    # Read more about jinja2 here:
    # http://docs.codenvy.com/user/tutorials/jinja2-tutorial/
    # http://jinja.pocoo.org/docs/dev/api/#basics
    # Render a jinja template
    @staticmethod
    def render_template(template_file_name, data,cookie_text=''):
        from jinja2 import Environment as JinjaEnv, PackageLoader as JinjaPL
        env = JinjaEnv(loader=JinjaPL('ntumc', 'templates'))
        template = env.get_template(template_file_name)

        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        if cookie_text:
            print(cookie_text)
        print(u"""Content-type: text/html; charset=utf-8\n""")
        print template.render(data)

        

    @staticmethod
    def search_form(omwcgi="wn-grid.cgi", lemma="",
                    langlist=[], interfacelang="eng",
                    langstring="Lang: ", lang2="eng", resize = 100):

        """Prints the html block of the OMW Search form and
        a dropdown for a list of available languages.
        The interface language is selected by default."""

        html = """<form method="post" style="display: inline-block" 
                   id="newquery" action="%s">
                  <span  style="font-size: %s%%">
                  <input style="font-size: %s%%" 
                   type="text" name="lemma" value="%s" 
                   size=8 maxlength=50>

        <button class="small"> <a href="javascript:{}"
           onclick="document.getElementById('newquery').submit(); 
           return false;"><span title="Search">
           <span style="color: #4D99E0;"><i class='icon-search'></i>
           </span></span></a></button>
 
         <strong>%s</strong><select name="lang" size="1" 
                                    style="font-size: %s%%"
              onchange="if(this.value == 'showmore') 
               toggle_visibility('langselect');">
          """ % (omwcgi, resize, resize, lemma,
                 langstring, resize)

        for l in langlist:
            if interfacelang == l:  # default language label
                html += """<option value ='%s' selected>%s
                        """ % (l, omwlang.trans(l, interfacelang))
            else:
                html += """<option value ='%s'>%s
                        """ % (l, omwlang.trans(l, interfacelang))

        html += """<option value="showmore">More...</option>"""
        html += """</select><select name="lang2" style="font-size: %s%%"
                    title="backoff language" size="1" 
                onchange="if(this.value == 'showmore') 
               toggle_visibility('langselect');">""" % resize

        for l in langlist:
            if l == lang2:  # default language label
                html += """<option value ='%s' selected>%s
                        """ % (l, omwlang.trans(l, interfacelang))
            else:
                html += """<option value ='%s'>%s
                        """ % (l, omwlang.trans(l, interfacelang))
        html += """<option value="showmore">More...</option>"""

        html += """</select></span></form>"""

        return html


    @staticmethod
    def language_selection(langselect, langlist=[], 
                           omwcgi="wn-grid.cgi", interfacelang="eng"):

        """Prints the html block of a hidden language selection
        with a list of all available languages. This is used to 
        restrict the number of languages displayed.
        The interface language is selected by default."""

        html = """<a onclick="toggle_visibility('langselect');">
                   <i class="icon-wrench"></i> Preferences</a>"""
        html += """<div id="langselect" style="display: none">"""
        html += """<span style="color: #4D99E0;display: inline-block; 
                    float:right">"""
        html += """
             <a href="javascript:{}"
             onclick="document.getElementById('langselection').submit(); 
             return false;"><span title="Update Language Selection">
             Update Language Selection
             </span></a></span><br>"""
        html += """<span style="color: #4D99E0;display: inline-block; 
                    float:right">"""
        html += """<input type="checkbox" 
             onclick="for(c in document.getElementsByName('langselect[]')) 
             document.getElementsByName('langselect[]').item(c).checked 
             = this.checked";> Select All/None</span>"""


        html += """<h6>Language Selection</h6>
                   <form  method="post" action="%s" 
                   id="langselection">""" % omwcgi
        html += """<table>"""

        for i, l in enumerate(sorted(langlist)):
            if i%5 == 0:
                html += """</tr><tr>"""
            if l in langselect:
                html += """<td><input type="checkbox" 
                            name="langselect[]" value="%s" checked> %s</td>
                        """ % (l, omwlang.trans(l, interfacelang))
            else:
                html += """<td><input type="checkbox" 
                        name="langselect[]" value="%s"> %s</td>
                    """ % (l, omwlang.trans(l, interfacelang))
        html += """</table>"""

        html += """<a href="javascript:{}"
             onclick="document.getElementById('langselection').submit(); 
             return false;"><span title="Update Language Selection"
             style="display: inline-block; float:right">
             <span style="color: #4D99E0;">Update Language Selection
             </span></span></a>"""
        html += """</form>"""
        html += """</div>"""

        return html


    @staticmethod
    def show_change_user_bttn(usrname, cgi="login.cgi?action=logout&target=tag-lexs.cgi"):
        """Prints the user status message, along 
           With a button to change it.
           The default cgi to refresh to is tag-lexs, 
           but it can be changed."""

        html = ""
        if usrname:
            html += """<form method=post target="_parent" 
             style="display: inline-block" action="%s">
             <strong>Current user:</strong>
             <font color="#3EA055">%s</font> 
             <input type ="hidden" name="usrname_cgi" value = "unknown">
             <input type = "submit" value = "Change"></form>
             """ % (cgi, usrname)
        else:
            html += """<form method = post target = "_parent" 
             style="display: inline-block" action = "%s">
             <strong>Current user:</strong>
             <font color="#CC0000">unknown</font>
             <input type ="hidden" name="usrname_cgi" value = "unknown">
             <input type = "submit" value = "Change"></form>
             """ % (cgi)
        return html

    @staticmethod
    def status_bar(user):
        """Prints a floating status bar (in the top right corner).
           This will display an Info Button, the User Status, and 
           a Home button."""

        html = ""
        dashboardcgi = "dashboard.cgi"

        html += """<span style="display: inline-block; float:right">
                  <ul class="button-bar">"""

        html += """<li><a class="tooltip-bottom"  data-content="#guidelines" 
              data-action="click"><span style="color: #4D99E0;">
                        <i class="icon-info-sign"></i></a></span></li>"""

        if user in valid_usernames:
            html += """<li><a disabled><span style="color: #4D99E0;">
                        <i class="icon-user"></i>%s</a></span></li> """ % user
        else:
            html += """<li><a title="Invalid User" disabled><span style="color: #bc5847;">
                        <i class="icon-user"></i></a></span></li> """

        html += """<li><a href="%s"><span style="color: #4D99E0;">
                   <i class="icon-home"></i></a></span></li>""" % dashboardcgi
        html += """</ul>"""
        html += """</span>"""

        return html


    @staticmethod
    def ne_bttn(usrname, 
                string2print = """<nobr><i class="icon-plus"></i>NE</nobr>"""):
        """Prints the Add New Named Entity button,
        taking as argument a username and an optional 
        string to be printed on the button."""

        tooltip = "Add a new Named Entity (quick entry)."
        addnecgi = "addne.cgi"
        html = """<form method= "post" style="display: inline-block; 
               margin: 0px; padding: 0px;" id="newNE"
               action="%s?usrname=%s"><a href="javascript:{}"
               onclick="document.getElementById('newNE').submit(); 
               return false;"><span title="%s" style="color: #4D99E0;">
               %s</span></a></form>
               """ % (addnecgi, usrname, tooltip, string2print)
        return html

    @staticmethod
    def hiderow_bttn(rowid, 
                string2print="<i class='icon-eye-close'></i>"):
        """Prints the Hide row button,
        taking as argument the rowid and an optional 
        string to be printed on the button."""

        tooltip = "Hide the row for '%s'." % rowid[10:]
        html = """<a href="javascript:{}"
               onclick="togglecol('%s')">
               <span title="%s" style="color:#4D99E0;">%s</a>
               """ % (rowid, tooltip, string2print)
        return html

    @staticmethod
    def hidecolumn_bttn(colid, 
                string2print=""):
        """Prints the Hide Column button,
        taking as argument the rowid and an optional 
        string to be printed on the button."""

        tooltip = "Hide the column '%s'." % colid
        html = """<a href="javascript:{}"
               onclick="togglecol('%s')">
               <i class='icon-eye-close'></i>%s</a>
               """ % (colid, string2print)
        return html


    @staticmethod
    def showallunder_bttn(elementid, 
                string2print="<i class='icon-eye-open'></i>"):
        """Prints the Show All button,
        taking as argument the element id that it on top of every
        other node to be displayed and an optional 
        string to be printed on the button."""

        tooltip = "Show hidden rows."
        html = """<a href="javascript:{}"
               onclick="showallunder('%s')">
               <span title="%s"style="color: #4D99E0;">%s</span></a>
               """ % (elementid, tooltip, string2print)
        return html


    @staticmethod
    def newsynset_bttn(usrname, synset="", 
                       string2print='<i class="icon-plus-sign"></i>'):
        """Prints the Add New Synset button,
        taking as argument a username, an optional related synset,  
        and an optional string to be printed on the button."""
        
        tooltip = ""
        if synset == "":
            tooltip = "Add a new synset to Wordnet."
        else:
            tooltip = "Add a new synset linked to %s." % synset

        addnewcgi = "addnew.cgi"

        html = """<form method="post" style="display: inline-block; 
               margin: 0px; padding: 0px;" id="newss%s"
               action="%s?usrname=%s&synset=%s"><a href="javascript:{}"
               onclick="document.getElementById('newss%s').submit(); 
               return false;"><span title="%s"style="color: #4D99E0;">
               %s</span></a></form>""" % (synset, addnewcgi, usrname, 
                                synset, synset, tooltip, string2print)
        return html

    @staticmethod
    def editsynset_bttn(usrname, synset, 
                        string2print='<i class="icon-edit"></i>'):
        """Prints the Edit Synset button,
        taking as argument a username, an optional related synset,  
        and an optional string to be printed on the button."""
        
        tooltip = "Edit %s (add lemmas, defs, etc.)" % synset
        editcgi = "annot-gridx.cgi"

        html = """<form method= "post" style="display: inline-block; 
               margin: 0px; padding: 0px;" id="editss%s"
               action="%s?usrname=%s&synset=%s"><a href="javascript:{}"
               onclick="document.getElementById('editss%s').submit(); 
                        return false;">
               <span  title="%s">%s</span></a>
               </form>""" % (synset, editcgi, usrname, 
                             synset, synset, tooltip, string2print)
        return html


    @staticmethod
    def multidict_bttn(lang1, lemma, 
                       string2print = '<i class="icon-book"></i>'):
        """Prints the Multidict button.
        Must have a language and a lemma as arguments. 
        The optional string2print will replace the value of the button"""

        tooltip = "Search '%s' in multiple dictionaries" % lemma
        multidictcgi = "multidict.cgi"
        html = """<form method= "post" style="display: inline-block; 
               margin: 0px; padding: 0px;" id="multidict"
               target="_blank" action="%s?lg1=%s&lemma1=%s">
               <a href="javascript:{}"
               onclick="document.getElementById('multidict').submit(); 
               return false;"><span title="%s" 
               style="color:#4D99E0;">%s</span></a>
               </form>""" % (multidictcgi, lang1, lemma, 
                             tooltip, string2print)
        return html


    @staticmethod
    def wordnet_footer():
        html = """<p><a href='http://compling.hss.ntu.edu.sg/omw/'>
               More detail about the wordnets</a>, including 
               links to the data, licenses and statistics about 
               the wordnets.<br> Maintainer: 
               <a href="http://www3.ntu.edu.sg/home/fcbond/">
               Francis Bond</a>&lt;<a href="mailto:bond@ieee.org">
               bond@ieee.org</a>&gt;</p>"""
        return html





    @staticmethod
    def show_sid_bttn(corpus,  sid, lemma):
        """Prints a sid: clickable to jump to context"""
        ## fixme lang1 lang2
        html = """<a class='sid' href='%s?corpus=%s&sid=%d&lemma=%s' 
target='log'>%d</a>""" % ('show-sent.cgi', corpus, sid, lemma, sid)
        return html

    @staticmethod
    def edit_sid_bttn(corpus, lang, usrname, sid, string2print = u"✎"):
        """Gives button to jump to the sentence in the edit interface"""
        html = """<a class='sid' target='_blank' 
href="%s?corpus=%s&lang%s&usrname=%s&sid=%s">%s</a>""" % ('tag-word.cgi', 
                                                          corpus, lang, 
                                                          usrname, sid,  
                                                          string2print)
        return html


    @staticmethod
    def googlespeech_text(lang, text):
        """This function takes some text, and outputs an HTML
        code that will use googlespeech to speak it when cliked.
        """
        if lang == "eng":
            l = "en"

        else:
            return text
# 
        html = """<span>
               <audio controls="controls" style="display:none;" autoplay="autoplay">
               <source src="http://translate.google.com/translate_tts?tl=%s&q=%s" type="audio/mpeg"/></audio></span>""" % (l,text)
        return html



class NTUMC_Cookies:

    @staticmethod
    def read_user_cookie(username = None, expire_hrs = 6):
        """Checks for a cookie object with user info, 
        if it fails to find, returns a cookie object
        where the user is set to 'unknown'.
        It takes a username argument (if available).
        The optional argument sets the expiration time
        for the cookie - the default is 6hrs.
        In order to work, this cookie must also be 
        written before the html header."""

        if 'HTTP_COOKIE' in os.environ:
            cookie_string = os.environ.get('HTTP_COOKIE')
            user_cookie = Cookie.SimpleCookie()
            user_cookie.load(cookie_string)

            if username:
                user_cookie["user_name"] = username
                # set to expire in 6 hrs
                user_cookie["user_name"]['expires'] = expire_hrs * 60 * 60  

        else:
            user_cookie = Cookie.SimpleCookie()
            user_cookie["user_name"] = 'unknown'

        return user_cookie
