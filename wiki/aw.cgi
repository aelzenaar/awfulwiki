#!/usr/bin/python3
# AwfulWiki - a badly hacked together wiki.
# URL: https://github.com/aelzenaar/awfulwiki
# Copyright (C) 2019 Alex Elzenaar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import cgi

import cgitb

from pathlib import Path
import re
import os

import markdown2

cgitb.enable()

# See http://wiki.c2.com/?JoinCapitalizedWords
re_validPageName = re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)")


def validPageName(page):
  """ Check whether the given page name is in WikiCase. """
  return False if re_validPageName.fullmatch(page) is None else True

def realPagePath(page):
  """ Given a page name, return the actual path in the filesystem. """
  return Path("data")/page

def myUrl():
  """ Return the URL of this script relative to the host. """
  return os.environ['SCRIPT_NAME']

def readablePageName(page):
  """ Split a WikiCase page name into separate words. """
  processed = page[0]
  for i in range(1, len(page)):
    if page[i].isupper():
      processed = processed + " "
    processed = processed + page[i]
  return processed

def skeleton(title, body, add_simplemde=False):
  """ Build the HTML for a response. """
  mathjax = """
            <script type="text/x-mathjax-config">
              MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]} });
            </script>
            <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML' async></script>
            """
  simplemde = """
              <link rel="stylesheet" href="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css">
              <script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
              """

  print("<html><head><title>{title}</title>{mathjax}{simplemde}</head>\
         <body>{body}</body></html>".format(title=title,
                                            body=body,
                                            mathjax=mathjax,
                                            simplemde=(simplemde if add_simplemde else "")))

def readPage(page):
  """ Return the full text of a page. """

  if not pageExists(page):
    return ""

  with realPagePath(page).open() as f:
    content = f.read()
  return content

def writePage(page, text):
  """ Overwrite the given page with new text, or delete the page if needed. """

  if text == "!delete":
    realPagePath(page).unlink()
    return False

  with realPagePath(page).open('w') as f:
    f.write(text)
  return True

def pageExists(page):
  """ Check whether the given page has been created before. """

  return realPagePath(page).exists()

def shipEditor(page):
  """ Return an HTML response with an editor for the given page. """

  text = readPage(page)
  skeleton(readablePageName(page) + " (editing)",
           """<h3>{formatPageName}</h3>
              <a href="{me}?page={pageName}">Abort Edit: Back to {formatPageName}</a>
              <form method="post" action="{me}?page={pageName}">
               <textarea id="newtext" name="newtext" cols="80" rows="24" wrap="virtual">{text}</textarea><br>
               <input type="submit" value="Save Changes">
              </form>
              <script>
                var simplemde = new SimpleMDE({{ element: document.getElementById("newtext") }});
              </script>""".format(me=myUrl(), pageName=page, formatPageName=readablePageName(page), text=text), True)

def shipPage(page):
  """ Return an HTML response with the content of the given page, doing any
      processing necessary (e.g. markdown)
  """

  text = markdown2.markdown(readPage(page),
                            extras=["link-patterns", "fenced-code-blocks"],
                            link_patterns=[(re_validPageName, r"{me}?page=\1".format(me=myUrl()))])

  skeleton(readablePageName(page),
           """<h3>{formatPageName}</h3>
              {text}

              <p><a href="{me}?page={pageName}&edit=1">Edit</a>&nbsp;<a href="{me}?page=MainPage">Home</a>
           """.format(me=myUrl(), pageName=page, formatPageName=readablePageName(page), text=text))


###
### Main
###
def main():
  """ Request entry point. """
  print("Content-Type: text/html")

  form = cgi.FieldStorage()

  if "page" not in form:
    page = "MainPage"
  else:
    page = form["page"].value
    if not validPageName(page):
      print("Status: 400 Bad Request")
      print()
      print("""<html><head><title>400 Bad Request</title></head><body>
               <h3>400 Bad Request</h3>
               <p>The server cannot or will not process the request due to something
               that is perceived to be a client error (e.g., malformed request syntax,
               invalid request message framing, or deceptive request routing).<p>In
               particular, the page title was not valid.<p><a href=\"{me}\">Home</a></body></html>""".format(me=myUrl()))
      quit()

  if "newtext" in form:
    if not writePage(page, form["newtext"].value):
      print("Status: 303 See Other")
      print("Location: {me}?page=MainPage".format(me=myUrl()))
      quit()

  do_edit = False
  if ("edit" in form and str(form["edit"].value) == "1") or not pageExists(page):
    do_edit = True

  print()

  if do_edit:
    shipEditor(page)
  else:
    shipPage(page)

main()
