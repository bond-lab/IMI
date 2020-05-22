#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi, os
import cgitb; cgitb.enable()




print("""\
Content-Type: text/html\n
<html><body>
<form enctype="multipart/form-data" action="ILIup.cgi" method="post">
<p>File: <input type="file" name="file"></p>
<p><input type="submit" value="Upload"></p>
</form>

OR BY URL
<form  action="ILIup.cgi" method="post">
<p>File: <input type="text" name="url"></p>
<p><input type="submit" value="Submit"></p>
</form>

</body></html>
""")
