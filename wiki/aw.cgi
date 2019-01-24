#!/usr/bin/python3
# AwfulWiki - a badly hacked together wiki.
# URL: https://github.com/aelzenaar/awfulwiki
# Copyright (C) 2019 Alex Elzenaar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cgi

import cgitb
cgitb.enable()

from pathlib import Path

import markdown2

def skeleton(title, body):
  print("<html><head><title>" + str(title) + "</title></head>")
  print("<body>")
  print(body)
  print("</body></html>")

def readPage(page):
  if not(pageExists(page)):
    return ""

  with (Path("data")/str(page)).open() as f:
    content = f.read()
  return content

def writePage(page, text):
  with (Path("data")/str(page)).open('w') as f:
    f.write(text)

def pageExists(page):
  return (Path("data")/str(page)).exists()

def shipEditor(page):
  text = readPage(page)
  skeleton(str(page) + " (editing)", "<h3>" + str(page) + "</h3>\n\n<a href=\"aw.cgi?page="+str(page)+"\">Abort Edit: Back to "+str(page)+"</a>\
           <form method=\"post\" action=\"aw.cgi?page="+str(page)+"\">\
             <textarea name=\"newtext\" cols=\"80\" rows=\"24\" wrap=\"virtual\">"+text+"</textarea><br>\
             <input type=\"submit\" value=\"Save Changes\">\
           </form>")

def shipPage(page):
  skeleton(str(page), "<h3>"+str(page)+"</h3>\n\n"+markdown2.markdown(readPage(page))+"\n\n<p><a href=\"aw.cgi?page="+str(page)+"&edit=1\">Edit</a>")


###
### Main
###

print("Content-Type: text/html")
print()

form = cgi.FieldStorage()

if "page" not in form:
  page = "MainPage"
else:
  page = form["page"].value

if "newtext" in form:
  writePage(page, form["newtext"].value)

do_edit = False
if ("edit" in form and str(form["edit"].value) == "1") or not(pageExists(page)):
  do_edit = True

if(do_edit):
  shipEditor(page)
else:
  shipPage(page)
