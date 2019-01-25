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
import re

import markdown2
import pygments

# See http://wiki.c2.com/?JoinCapitalizedWords
re_validPageName = re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)")
def validPageName(page):
  return False if re_validPageName.fullmatch(page) == None else True

def realPagePath(page):
  return Path("data")/page

def readablePageName(page):
  processed = page[0]
  for i in range(1,len(page)):
    if(page[i].isupper()):
      processed = processed + " "
    processed = processed + page[i]
  return processed

def skeleton(title, body, add_simplemde=False):
  mathjax   = """
              <script type="text/x-mathjax-config">
                MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]} });
              </script>
              <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML' async></script>
              """
  simplemde = """
              <link rel="stylesheet" href="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css">
              <script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
              """

  print("<html><head><title>{title}</title>{mathjax}{simplemde}</head><body>{body}</body></html>".format(title=title,
                                                                                                        body=body,
                                                                                                        mathjax=mathjax,
                                                                                                        simplemde=(simplemde if add_simplemde else "")))

def readPage(page):
  if not(pageExists(page)):
    return ""

  with realPagePath(page).open() as f:
    content = f.read()
  return content

def writePage(page, text):
  if(text == "!delete"):
    realPagePath(page).unlink()
    return False

  with realPagePath(page).open('w') as f:
    f.write(text)
  return True

def pageExists(page):
  return realPagePath(page).exists()

def shipEditor(page):
  text = readPage(page)
  skeleton(readablePageName(page) + " (editing)",
           """<h3>{formatPageName}</h3>
              <a href="aw.cgi?page={pageName}">Abort Edit: Back to {formatPageName}</a>
              <form method="post" action="aw.cgi?page={pageName}">
               <textarea id="newtext" name="newtext" cols="80" rows="24" wrap="virtual">{text}</textarea><br>
               <input type="submit" value="Save Changes">
              </form>
              <script>
                var simplemde = new SimpleMDE({{ element: document.getElementById("newtext") }});
              </script>""".format(pageName=page, formatPageName=readablePageName(page), text=text), True)

def shipPage(page):
  text = markdown2.markdown(readPage(page), extras=["link-patterns", "fenced-code-blocks"], link_patterns=[(re_validPageName, r"aw.cgi?page=\1")])

  skeleton(readablePageName(page),
           """<h3>{formatPageName}</h3>
              {text}

              <p><a href="aw.cgi?page={pageName}&edit=1">Edit</a>&nbsp;<a href="aw.cgi?page=MainPage">Home</a>
           """.format(pageName=page, formatPageName=readablePageName(page), text=text))


###
### Main
###

print("Content-Type: text/html")

form = cgi.FieldStorage()

if "page" not in form:
  page = "MainPage"
else:
  page = form["page"].value
  if not validPageName(page):
    print("Status: 400 Bad Request")
    print()
    print("<html><head><title>400 Bad Request</title></head><body><h3>400 Bad Request</h3><p>The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing).<p>In particular, the page title was not valid.<p><a href=\"aw.cgi\">Home</a></body></html>")
    quit()

if "newtext" in form:
  if not writePage(page, form["newtext"].value):
    print("Status: 303 See Other")
    print("Location: aw.cgi?page=MainPage")
    quit()

do_edit = False
if ("edit" in form and str(form["edit"].value) == "1") or not(pageExists(page)):
  do_edit = True

print()

if(do_edit):
  shipEditor(page)
else:
  shipPage(page)
