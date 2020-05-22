#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi, os
import cgitb; cgitb.enable()
import html
import urllib


# try: # Windows needs stdio set for binary mode.
#     import msvcrt
#     msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
#     msvcrt.setmode (1, os.O_BINARY) # stdout = 1
# except ImportError:
#     pass

form = cgi.FieldStorage()

# A nested FieldStorage instance holds the file
try: 
    fileitem = form['file']


    # Test if the file was uploaded
    if fileitem.filename:

        # strip leading path from file name to avoid directory traversal attacks
        fn = os.path.basename(fileitem.filename)
        with open('files/' + fn, 'wb') as file:
            file.write(fileitem.file.read())

        fname = fileitem.filename
        if fname.endswith('.js'):
            with open('files/' + fileitem.filename, 'r') as f:
                message = cgi.escape(f.read(), True).replace('\n', '<br>')

        else:
            message = 'The file "' + fn + '" was uploaded successfully'


    else:
        message = 'No file was uploaded'

except:
    pass




try: 

    fileurl = form.getvalue('url')
    message = "Saw the url" #TEST

    if fileurl:
        filehandle = urllib.urlopen(fileurl)
        message = "downloaded the url" #TEST

        # Wilson: This would break with trailing /
        fn = fileurl.split('/')[-1]
        message = "Got the file name: %s" % fn #TEST

        open('files/' + fn, 'wb').write(filehandle.read())
        message = "Copied the file" #TEST

        if fn.endswith('.js'):
            with open('files/' + fn, 'r') as f:
                message = cgi.escape(f.read(), True).replace('\n', '<br>')

        else:
            message = 'The file "' + fn + '" was uploaded successfully'

    else:
        message = 'No file was uploaded'

except:
    pass






try:
   
    print("""\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % html.escape(message))

except:
    print("""\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % ('Something went wrong...'))

