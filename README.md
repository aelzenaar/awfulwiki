# AwfulWiki

This piece of software is a nasty hacked together semi-clone of [WikiWikiWeb](http://wiki.c2.com).

## Dependencies

 * **Web server.** You need [thttpd](http://www.acme.com/software/thttpd/); then run `./run.sh`, and click on `aw.cgi` in the directory listing.
 * **Markdown support.** You need [markdown2](https://github.com/trentm/python-markdown2) installed locally. Some patches which might make awfulwiki use
   easier can be found [in my fork](https://github.com/aelzenaar/python-markdown2).
 * **Pretty text editing.** AwfulWiki embeds [SimpleMDE](https://github.com/sparksuite/simplemde-markdown-editor). It need not be installed locally.
 * **LaTeX support.** AwfulWiki embeds [MathJax](https://https://www.mathjax.org/). It need not be installed locally.
