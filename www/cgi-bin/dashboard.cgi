#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import re, sqlite3, collections
import os, http.cookies, datetime  # for cookies
from collections import defaultdict as dd

from ntumc_gatekeeper import concurs
from ntumc_webkit import *  # to import HTML blocks
from lang_data_toolkit import *  # to import langs and dictionaries data and functions

from passlib.hash import pbkdf2_sha256

# Fixes encoding issues when reading cookies from os.environ
import os, sys
from importlib import reload
sys.getfilesystemencoding = lambda: 'utf-8'
reload(os)


form = cgi.FieldStorage()
user = form.getvalue("user", "")

pw = form.getvalue("pw", "")
old_pw = form.getvalue("old_pw", "")  # for pw change
new_pw = form.getvalue("new_pw", "")  # for pw change


cgi_mode = form.getvalue("cgi_mode", "")

### reference to self (.cgi)
selfcgi = "dashboard.cgi"

# ### reference to search interface
# omwcgi = "wn-gridx.cgi?usrname=%s&gridmode=%s" % (usrname, gridmode)

### ADMIN.DB

admindb = "admin.db"
logged = False
#user='fcbond'

message_log = ""
hashed_pw = ""





################################################################
# FETCH / CLEAR COOKIES
################################################################
if 'HTTP_COOKIE' in os.environ:
    C = http.cookies.SimpleCookie(os.environ['HTTP_COOKIE'])
else:
    C = http.cookies.SimpleCookie()

# Irregardless of existing or not existing previous information,
# If the cgi_mode = logout, it overwrites user and pw
if cgi_mode == "logout":
    C["UserID"] = "logout"
    C["Password"] = "logout"

# If no user + password was given (i.e. if no one tried to login)
if user == "" and pw == "":
    # Check if there is an user
    if 'UserID' in C:
        user = C['UserID'].value
    else:
        user = "logout"

    # Check if there is a password (hashed)
    if 'Password' in C:
        hashed_pw = C['Password'].value
    else:
        hashed_pw = "logout"



################################################################
# UPDATE PASSWORD
################################################################
if cgi_mode == "update_pw":

    conn_admin, admin = concurs(admindb)

    pws = dict()
    admin.execute("""SELECT username, password
                  FROM  users
                  WHERE username = ? """, (user,))
    for username, password in admin:
        pws[username] = password

    try:  # this protects against invalid usernames

        # message_log += "The old_pw: %s<br>" % old_pw  #TEST
        # message_log += "The new_pw: %s<br>" % new_pw  #TEST

        if pbkdf2_sha256.verify(old_pw, pws[user]):  # check old 1st
            # message_log += "The old pw check passed!<br>"  #TEST

            # Create & update hash in the database
            hashpw = pbkdf2_sha256.encrypt(new_pw, rounds=20000,
                              salt_size=16)
            admin.execute("""UPDATE users SET password = ?
              WHERE username = ? """,  [hashpw, user])

            conn_admin.commit()  # Save changes to database
            message_log += "Your password was updated!" 

    except:
        message_log += "Something went wrong!<br>" 
        message_log += "The password was not changed. Try again..."

    conn_admin.close()  # Close database

################################################################
# TRY TO LOGIN (CONNECT TO ADMIN.DB)
################################################################
if user != "logout":
    conn_admin, admin = concurs(admindb)

    query = """SELECT username, password
               FROM  users
               WHERE username = ? """
    #print(query, user)
    admin.execute(query, (user,))
    #message_log += """<br>Queried: '%s' """ % query  #TEST


    pws = dict()
    for username, password in admin:
        pws[username] = password
    #message_log += """<br>PWS(dict): '%s' """ % pws  #TEST



    # message_log += "<br>Cookie hashed_pw: %s" % hashed_pw  #TEST
    # try:
    #     message_log += "<br>Hashed_pw in db: %s" % pws[user]  #TEST
    # except:
    #     message_log += "<br>Something was wrong with the username."  #TEST


    try:  # this protects against invalid usernames
        if pbkdf2_sha256.verify(pw, pws[user]):
            logged = True
            hashed_pw = pws[user]
        elif pws[user] in hashed_pw:
            logged = True
        else:
            user = "logout"
            hashed_pw = "logout"

    except:
        user = "logout"
        hashed_pw = "logout"

################################################################
# HTML
################################################################

C["UserID"] = user
C["Password"] = hashed_pw
expires = datetime.datetime.utcnow() + datetime.timedelta(days=30) # expires in 30 days
C['UserID']['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
C["Password"]["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

print(NTUMC_Cookies.secure(C))
print("""Content-type: text/html; charset=utf-8\n\n""")
print("""<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
    <title>%s</title>

    <script type="text/javascript">
       function toggle_visibility(id) {
           var e = document.getElementById(id);
           if(e.style.display == 'block')
              e.style.display = 'none';
           else
              e.style.display = 'block';
       }
    </script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="../HTML-KickStart-master/js/kickstart.js"></script> <!-- KICKSTART -->
    <link rel="stylesheet" href="../HTML-KickStart-master/css/kickstart.css" media="all" /> <!-- KICKSTART -->


  </head>
  <body>""" % 'Dashboard - NTUMC Tagging Tools' if logged else 'Login')

print(message_log)
if logged:

    # TOP RIGHT LOGOUT
    print(u"""<br><span style="position: fixed; top: 10px; right: 5px;"><a href="%s?cgi_mode=logout">
              <button class="small">
              Logout</button></a></span>""" % selfcgi)


    print("""<b>Welcome %s!</b><br><br>""" % user)

    print("""<!-- Tabs Left -->
             <ul class="tabs left">
               <li><a href="#welcome">Welcome</a></li>
               <li><a href="#wntools">Wordnet Tools</a></li>
               <li><a href="#corpustools">Corpus Tools</a></li>
               <li><a href="#changepw"><i class="icon-pencil">
                   </i> User Preferences</a></li>
<!--               <li><a href="#tabr3">Tab3</a></li> -->
              </ul>""")

# <div id="tabr1" class="tab-content">Tab1</div>
# <div id="tabr2" class="tab-content">Tab2</div>
# <div id="tabr3" class="tab-content">Tab3</div>""")

    # print """<!-- Button Bar w/icons --><ul class="button-bar">
    #          <li><a onclick="toggle_visibility('changepw');">
    #              <i class="icon-pencil"></i> User Preferences</a></li>
    #          <li><a href=""><i class="icon-tag"></i> Tag</a></li>
    #          <li><a href=""><i class="icon-upload-alt"></i> Upload</a></li>
    #          <li><a href=""><i class="icon-plus-sign"></i></a></li>
    #          </ul>"""

    # print("""<button onclick="toggle_visibility('changepw');">
    #           Change PW</button>""")

    # WELCOME
    print("""<div id="welcome" class="tab-content">
             <b>Welcome to NTUMC Tagging Tools!</b>
             <br>Use the menu above to navigate the existing tools.
             </div>""")

    # WORDNET TOOLS
    print("""<div id="wntools" class="tab-content">
             <b>These are the available Wordnets Views!</b>
             <br><br><div style="width: 300px">
             <ul class="menu vertical">
<!--                <li><a href="">  -->
<!--                    Open Multilingual Wordnet</a>  -->
<!--                  <ul><li><a href="wn-gridx.cgi?gridmode=grid">  -->
<!--                          Original</a></li>  -->
<!--                      <li><a href="wn-gridx.cgi?gridmode=gridx">  -->
<!--                          Extended</a></li>  -->
<!--                  </ul>  -->
               <li><a href="wn-gridx.cgi?gridmode=ntumcgrid">
                   NTUMC Wordnet (Ongoing)</a></li>
               <li><a href="dlogs.cgi">Wordnet Editing Logs</a></li>

               <li><a href="wn-gridx.cgi?gridmode=cow">
                   Chinese Open Wordnet</a></li>
               <li><a href="wn-gridx.cgi?gridmode=wnja">
                   Japanese Wordnet</a></li>
               <li><a href="wn-gridx.cgi?gridmode=wnbahasa">
                   Wordnet Bahasa</a></li>
 <!--               <li><a href="mapwn16_30.cgi"> -->
<!--                    WN1.6 to WN 3.0 Converter</a></li> -->


             </ul></div></div>""")

    # CORPUS TOOLS
    print("""<div id="corpustools" class="tab-content">
             <b>These are the available Corpus Tools!</b>
             <br><br><div style="width: 300px">
             <ul class="menu vertical">
               <li><a href="#">Taggers</a>

                 <ul><li><a href="#">Lexical Tagger</a>
                      <ul><li><a href="tag-lexs.cgi?gridmode=ntumcgrid&corpus=eng&lang=eng" target='_blank'>
                              English</a></li>
                          <li><a href="tag-lexs.cgi?gridmode=ntumcgrid&corpus=cmn&lang=cmn" target='_blank'>
                              Mandarin</a></li>
                          <li><a href="tag-lexs.cgi?gridmode=ntumcgrid&corpus=jpn&lang=jpn" target='_blank'>
                              Japanese</a></li>
                          <li><a href="tag-lexs.cgi?gridmode=ntumcgrid&corpus=ind&lang=ind" target='_blank'>
                              Indonesian</a></li>
                          <li><a href="tag-lexs.cgi?gridmode=ntumcgrid&corpus=ita&lang=ita" target='_blank'>
                              Italian</a></li>
                       </ul></li>


                     <li><a href="#">Sentence Tagger</a>
                     <ul><li><a href="tag-word.cgi?gridmode=ntumcgrid&corpus=eng&lang=eng" target='_blank'>
                             English</a></li>
                         <li><a href="tag-word.cgi?gridmode=ntumcgrid&corpus=cmn&lang=cmn" target='_blank'>
                             Mandarin</a></li>
                         <li><a href="tag-word.cgi?gridmode=ntumcgrid&corpus=jpn&lang=jpn" target='_blank'>
                             Japanese</a></li>
                         <li><a href="tag-word.cgi?gridmode=ntumcgrid&corpus=ind&lang=ind" target='_blank'>
                             Indonesian</a></li>
                         <li><a href="tag-word.cgi?gridmode=ntumcgrid&corpus=ita&lang=ita" target='_blank'>
                             Italian</a></li>
                      </ul></li>


                     <li><a href="#">Sentiment Chunk Tagger</a>
                     <ul><li><a href="tag-senti.cgi?lang=eng" target='_blank'>
                             English</a></li>
                         <li><a href="tag-senti.cgi?lang=cmn" target='_blank'>
                             Mandarin</a></li>
                         <li><a href="tag-senti.cgi?lang=jpn" target='_blank'>
                             Japanese</a></li>
                         <li><a href="tag-senti.cgi?lang=ind" target='_blank'>
                             Indonesian</a></li>
                         <li><a href="tag-senti.cgi?lang=ita" target='_blank'>
                             Italian</a></li>
                      </ul></li>




                     <li><a href="fix-corpus.cgi?editv=True" target='_blank'>
                          Corpus Fixer</a></li>
                 </ul>



               <li><a href="agreement.cgi">Agreement Analysis</a></li>

               <li><a href="sent-linking.cgi">Sentence Links</a></li>

               <li><a href="showcorpus.cgi">Corpus Browser</a></li>

               <li><a href="corpus-sum.cgi">Corpus Summary</a></li>

               <li><a href="corpus-qc.cgi?corpus=eng&sid_from=10000&sid_to=12000">Corpus Quality Control (slowish)</a></li>

               <li><a href="tag-log.cgi?days=7">Tagging Log (7 days)</a>

               <li><a href="tag-status.cgi">Tagging Status</a>
               <ul><li><a>English</a>
                       <ul><li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/eng.db&sid_from=10000&sid_to=12000">
                                 Stories</a>

                             <ul>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=10000&sid_to=10999">
                                 Speckled Band</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=11000&sid_to=11899">
                                 Dancing Men</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=55657&sid_to=56209">
                                 The Red-Headed Leaugue</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=50804&sid_to=51464">
                                 A Scandal In Bohemia</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=45681&sid_to=48504">
                                 The Hound of the Baskervilles       (I&ndash;III)</a>
                                 </li>

                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/eng.db&sid_from=11900&sid_to=11999">
                                 The Spider's Thread</a>
                                 </li>
                             </ul> 


                           </li>
                             <li><a target='_blank' href="tag-status.cgi?db=""" +
                        """../db/eng.db&sid_from=100000&sid_to=110000">
                                 YourSing</a></li>
                             <li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/eng.db">All</a></li>
                         </ul>
                       </li></li>


                     <li><a>Chinese</a>
                         <ul><li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/cmn.db&sid_from=10000&sid_to=12000">
                                 Stories</a>

                             <ul>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/cmn.db&sid_from=10000&sid_to=10999">
                                 Speckled Band</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/cmn.db&sid_from=11000&sid_to=11899">
                                 Dancing Men</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/cmn.db&sid_from=11900&sid_to=11999">
                                 The Spider's Thread</a>
                                 </li>
                             </ul> 



                             </li>

                             <li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/cmn.db&sid_from=100000&sid_to=110000">
                                 YourSing</a></li>
                             <li><a target='_blank'  href="tag-status.cgi?db=""" +
                        """../db/cmn.db">All</a></li>
                         </ul>
                       </li></li>




                     <li><a>Japanese</a>
                         <ul><li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/jpn.db&sid_from=10000&sid_to=12000">
                                 Stories</a>

                             <ul>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/jpn.db&sid_from=10000&sid_to=10999">
                                 Speckled Band</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/jpn.db&sid_from=11000&sid_to=11899">
                                 Dancing Men</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/jpn.db&sid_from=11900&sid_to=11999">
                                 The Spider's Thread</a>
                                 </li>
                             </ul> 



                             </li>

                             <li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/jpn.db&sid_from=100000&sid_to=110000">
                                 YourSing</a></li>
                             <li><a target='_blank'  href="tag-status.cgi?db=""" +
                        """../db/jpn.db">All</a></li>
                         </ul>
                       </li></li>




                     <li><a>Indonesian</a>
                         <ul><li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/ind.db&sid_from=10000&sid_to=12000">
                                 Stories</a>

                             <ul>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/ind.db&sid_from=10000&sid_to=10999">
                                 Speckled Band</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/ind.db&sid_from=11000&sid_to=11899">
                                 Dancing Men</a>
                                 </li>
                                 <li><a target='_blank' href="tag-status.cgi?db=""" +
                                 """../db/ind.db&sid_from=11900&sid_to=11999">
                                 The Spider's Thread</a>
                                 </li>
                             </ul> 


                             </li>

                             <li><a  target='_blank' href="tag-status.cgi?db=""" +
                        """../db/ind.db&sid_from=100000&sid_to=110000">
                                 YourSing</a></li>
                             <li><a target='_blank'  href="tag-status.cgi?db=""" +
                        """../db/ind.db">All</a></li>
                         </ul>
                       </li></li>

                 </ul>



               <li><a href="">POS Distribution</a>

                 <ul>
                     <li><a href="">English</a>: 
                        <ul>
                        <li> <a href="pos-sum.cgi?lang=eng&tagset=pos">POS</a>
                        <li> <a href="pos-sum.cgi?lang=eng&tagset=upos">UPOS</a>
                        </ul>
                     </li>


                      <li><a href="">Chinese</a>
                         <ul><li><a href="pos-sum.cgi?lang=cmn&tagset=pos">
                                 POS </a></li>
                             <li><a href="pos-sum.cgi?lang=cmn&tagset=upos">
                                 UPOS </a></li>
                         </ul>
                       </li></li>

                 </ul>



             </ul></div></div>""")

    # USER PREFERENCES
    print("""<div id="changepw" class="tab-content">
             <b>Update your password here:</b>""")
    print("""<br><br><form action="%s" method="post"">
	     <input name="cgi_mode" value="update_pw" type="hidden"/>
	     <input name="user" value="%s" type="hidden"/>
	     <input name="old_pw" placeholder="old password" 
              type="password" required/>
	     <input name="new_pw" type="password"
              placeholder="new password" required/>
          """ % (selfcgi, user))
    print("""<input type="submit" value="Change Password"/>
             </form></p></div>""")


else:
    print("You need to login before accessing to the tools.")
    print("""<form action="%s" method="post"">
	     <input name="user" placeholder="username" required/>
	     <input name="pw" type="password"
              placeholder="password" required/>
          """ % (selfcgi,))

    # Submit button
    print("""<br><input type="submit" value="Login"/></form></p>""")


# Print Footer
# print "<hr><p>"
print(HTML.wordnet_footer())  # Footer

print("""<p>Source code hosted on github: <a href='https://github.com/bond-lab/IMI'>https://github.com/bond-lab/IMI</a></p>
""")

### Close HTML
print("""</body>
         </html>""")
