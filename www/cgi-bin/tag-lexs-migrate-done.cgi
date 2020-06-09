#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Wilson(FIXME): Undefined vars: user_cookie, valid_usernames, wncgi, HTML, 
#   tagcgi, corpus, lemma, ss, lang, lim, com_all, lss, sfcorpus, omwcgi, ss,
#   lang, lemma

########## HTML

### Checked User Cookie (above), and now prints it ('unknown' will be de default) 
print(user_cookie)
### Header
print(u"""Content-type: text/html; charset=utf-8\n""")


# ; padding:15px;
print("""<table style="width:100%;">
<tr>
  <td valign="top" style="width:50%">""")
 
print("""</td> <td align="right" style="width:50%">""")

### USER COOKIE
try:
    usrname = user_cookie['user_name'].value

    if usrname in valid_usernames:
        pass

    else:
        print("""<strong>NTUMC Annotation Tools</strong>""")
        print("""<br><strong>A valid user has not been defined or it has expired.</strong><br>""")
        print("""Please choose a valid username to continue!""")
        print("""<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % wncgi)

except KeyError:
    print("""<strong>NTUMC Annotation Tools</strong>""")
    print("""<br><strong>I couldn't find a username in the cookie!</strong><br>""")
    print("""Please choose a valid username to continue!""")
    print("""<form method = post action = "%s"> username:<input type ="text" name="usrname_cgi"> 
                 <input type = "submit" value = "Change"> </form> """ % wncgi)


print(""" </td> </tr>""") # closes first row 

# No Username No Page!
if usrname not in valid_usernames:
    print("""</td> <td style="width:55%"> <br><br> </td> </tr> </table>""") # closes first row 

else:
    # Print user status
    print("""<tr>""" + HTML.show_change_user_bttn(usrname))

    print("""<td valign="top" style="width:55%; border-right: 1px solid black">""") # second row
    print("""<iframe name="tagging" src="%s?corpus=%s&lemma=%s&ss=%s&lang=%s&lim=%d&com_all=%s&lmss=%s&sfcorpus=%s&usrname=%s"
              frameborder="0" width="100%%" id="tag-lexiframe" onload="resizeAllFrames()"></iframe>
          """ % (tagcgi, corpus, lemma, ss, lang, lim, com_all, lmss, sfcorpus, usrname))

    print("""</td>""") # closes first column of second row


    print(""" <td valign="top" style="width:45%%"> <table style="width:100%%"><tr><td>
    <iframe name="wn" id="omwiframe" src="%s?ss=%s&lang=%s&lemma=%s&usrname=%s&gridmode=ntumcgrid" frameborder="0" 
     width="100%%" onload="resizeAllFrames()" ></iframe></td></tr>
         """ % (omwcgi, ss, lang, lemma, usrname))


    print("""<tr> 
             <td valign="top" style="width:45%"><hr>
             <iframe name="log" id="logiframe" frameborder="0"
              width="100%" onload="resizeAllFrames()" ></iframe>
             </td></tr></table>
             </td></tr></table>""")
