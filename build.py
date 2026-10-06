#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the CRISiSLab-hosted AJDTS site from the archived Massey original.

    python3 build.py

Reads  original/   a pristine mirror of https://psychlab.massey.ac.nz/trauma/
       new-issue/   PDFs for issues CRISiSLab hosts itself
       issues.py    metadata for those issues
Writes site/        the deployable static site

Everything AJDTS published up to Volume 28 keeps living on the archived Massey
server: links to those PDFs are rewritten to absolute psychlab.massey.ac.nz
URLs that open in a new tab. Only the issues listed in issues.py are served
from here.
"""

import html
import os
import posixpath
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from issues import ISSUES, UPDATED  # noqa: E402

ORIGINAL = os.path.join(HERE, "original")
NEW_ISSUE = os.path.join(HERE, "new-issue")
SITE = os.path.join(HERE, "site")

ARCHIVE = "https://psychlab.massey.ac.nz/trauma"
CRISISLAB = "https://www.crisislab.org.nz"

# Pages that exist in this mirror. Anything else a link points at still lives
# on the archived Massey server.
LOCAL_PAGES = {
    "index.html",
    "style.css",
    "crisislab.css",
    "info/about.html",
    "info/submissions.html",
    "info/editorial-board.html",
    "info/contact.html",
    "info/copyright.htm",
    "issues/current.html",
    "issues/previous.html",
    "links/webindex.html",
}

# Links the original site got slightly wrong, or that we renamed.
ALIASES = {
    "info/copyright.html": "info/copyright.htm",
    # A commented-out "Contact" menu item on every page pointed at a contact.html
    # that never existed beside it. Aim it at the real page in case it is ever
    # uncommented.
    "contact.html": "info/contact.html",
    "issues/contact.html": "info/contact.html",
    "links/contact.html": "info/contact.html",
}
ALIASES.update({"issues/%s/contact.html" % i["dir"]: "info/contact.html" for i in ISSUES})

HTML_PAGES = [
    "index.html",
    "info/about.html",
    "info/submissions.html",
    "info/editorial-board.html",
    "info/contact.html",
    "info/copyright.htm",
    "issues/current.html",
    "issues/previous.html",
    "links/webindex.html",
]

CURRENT = ISSUES[0]
LOCAL_PREFIXES = ("images/",) + tuple("issues/%s/" % i["dir"] for i in ISSUES)


# --------------------------------------------------------------------------
# link rewriting
# --------------------------------------------------------------------------

URL_ATTR = re.compile(r'\b(href|src)="([^"]*)"', re.I)
SKIP = re.compile(r"^(https?:|mailto:|javascript:|data:|tel:|//|#)", re.I)


def rewrite_urls(markup, page):
    """Point every link at this mirror or at the Massey archive, as applicable."""
    base = posixpath.dirname(page) or "."

    def repl(m):
        attr, url = m.group(1), m.group(2)
        if not url or SKIP.match(url):
            return m.group(0)
        path, _, frag = url.partition("#")
        frag = "#" + frag if "#" in url else ""
        if not path:
            return m.group(0)
        target = posixpath.normpath(posixpath.join(base, path))
        target = ALIASES.get(target, target)
        if target in LOCAL_PAGES or target.startswith(LOCAL_PREFIXES):
            return '%s="%s%s"' % (attr, posixpath.relpath(target, base), frag)
        return '%s="%s/%s%s"' % (attr, ARCHIVE, target, frag)

    return URL_ATTR.sub(repl, markup)


A_TAG = re.compile(r'<a\s+([^>]*href="https?://[^"]*"[^>]*)>', re.I)


def open_external_in_new_tab(markup):
    """Links that leave this mirror must escape the Wix iframe."""
    def repl(m):
        attrs = m.group(1)
        if "target=" in attrs.lower():
            return m.group(0)
        return '<a %s target="_blank" rel="noopener">' % attrs.rstrip()

    return A_TAG.sub(repl, markup)


# --------------------------------------------------------------------------
# chrome: notice banner, stylesheet, working search box
# --------------------------------------------------------------------------

def notice(depth):
    """depth = number of '../' steps back to the site root."""
    up = "../" * depth
    return """
        <div id="crisislab-notice">
          <p><strong>A note on this site.</strong> The <em>Australasian Journal of Disaster and
          Trauma Studies</em> website hosted by Massey University&rsquo;s School of Psychology has been
          archived. <a href="{crisislab}">CRISiSLab</a> is hosting this temporary mirror so that
          <a href="{up}issues/current.html">{label}</a> can be published and downloaded.
          Every issue up to and including Volume 28, Number 1 is still served from the
          <a href="{archive}/">archived Massey site</a>, and the links on the
          <a href="{up}issues/previous.html">Previous Issues</a> page will take you there.</p>
        </div>
""".format(crisislab=CRISISLAB, archive=ARCHIVE, up=up, label=html.escape(CURRENT["label"]))


FOOTER_DOMAIN = re.compile(
    r'<span><a href="(?:\.\./)*index\.html">trauma\.massey\.ac\.nz</a></span>')
FOOTER_DATE = re.compile(r'(<!-- #BeginDate format:Sw1 -->).*?(<!-- #EndDate -->)', re.S)


def fix_footer(markup):
    markup = FOOTER_DOMAIN.sub(
        '<span><a href="%s/">trauma.massey.ac.nz</a></span>'
        '<span>Hosted by <a href="%s">CRISiSLab</a></span>' % (ARCHIVE, CRISISLAB),
        markup, count=1)
    markup = FOOTER_DATE.sub(lambda m: m.group(1) + UPDATED + m.group(2), markup, count=1)
    return markup


SEARCH_FORM = re.compile(r'<form id="searchform".*?</form>', re.S | re.I)

# The original pointed at google.com/custom with a sitesearch for the long-dead
# www.massey.ac.nz/~trauma path. Search the archive instead.
NEW_SEARCH_FORM = """<form id="searchform" name="searchform" method="get" action="https://www.google.com/search" target="_blank" rel="noopener" onsubmit="document.getElementById('ajdts-q').value='site:psychlab.massey.ac.nz/trauma '+document.getElementById('ajdts-terms').value;">
			 <div class="fieldcontainer">
              <input type="hidden" name="q" id="ajdts-q" />
              <input type="text" id="ajdts-terms" class="searchfield" placeholder="Search AJDTS" />
			  <input type="submit" name="searchbtn" id="searchbtn" value="">
			 </div><!-- @end .fieldcontainer -->
           </form>"""

# Wix HTML components are fixed-height. Tell the host page how tall we are so
# Velo can resize the component (see README). Harmless when not embedded.
EMBED_JS = """<script>
(function () {
	if (window.parent === window) { return; }
	function postHeight() {
		try {
			window.parent.postMessage(
				{ ajdtsHeight: document.documentElement.scrollHeight }, "*");
		} catch (e) {}
	}
	window.addEventListener("load", postHeight);
	window.addEventListener("resize", postHeight);
	setTimeout(postHeight, 300);
	setTimeout(postHeight, 1500);
})();
</script>
"""


STYLE_LINK = re.compile(r'(<link rel="stylesheet" type="text/css" href=")([^"]*style\.css)(" ?/?>)', re.I)


def add_chrome(markup, page):
    depth = page.count("/")
    up = "../" * depth
    markup = STYLE_LINK.sub(
        lambda m: m.group(0) + '\n<link rel="stylesheet" type="text/css" href="%scrisislab.css" />' % up,
        markup, count=1)
    markup = SEARCH_FORM.sub(lambda m: NEW_SEARCH_FORM, markup, count=1)
    markup = fix_footer(markup)
    markup = markup.replace('<div id="container">', notice(depth) + '\n       <div id="container">', 1)
    markup = markup.replace("</body>", EMBED_JS + "</body>", 1)
    return markup


# --------------------------------------------------------------------------
# page content for the issues we host
# --------------------------------------------------------------------------

def paper_listing(issue, prefix):
    """Author/title/keyword listing, as used on the Current Issue page."""
    out = []
    for section in issue["sections"]:
        out.append('            <h4>%s</h4>' % section["heading"])
        for p in section["papers"]:
            out.append('            <h5><a class="pdf" href="%s%s">%s</a></h5>' % (prefix, p["pdf"], p["title"]))
            out.append('            <p><em>%s</em></p>' % p["authors"])
            out.append('            <p><strong>Keywords: </strong>%s</p>' % p["keywords"])
    return "\n".join(out)


def paper_listing_with_abstracts(issue, prefix):
    out = []
    for section in issue["sections"]:
        out.append('            <h4>%s</h4>' % section["heading"])
        for p in section["papers"]:
            out.append('            <h5><a class="pdf" href="%s%s">%s</a></h5>' % (prefix, p["pdf"], p["title"]))
            out.append('            <p><em>%s</em></p>' % p["authors"])
            out.append('            <p><strong>Keywords: </strong>%s</p>' % p["keywords"])
            out.append('            <blockquote>')
            out.append('              <p><strong>Abstract</strong>:<br />')
            out.append('              %s</p>' % p["abstract"])
            out.append('            </blockquote>')
    return "\n".join(out)


def downloads_block(issue, prefix):
    lines = ['            <h5><a href="%s%s">%s</a> (complete issue, PDF)</h5>'
             % (prefix, issue["full_pdf"], issue["label"])]
    if issue.get("contents_pdf"):
        lines.append('            <p><a href="%s%s">Contents page - %s</a></p>'
                     % (prefix, issue["contents_pdf"], issue["label"]))
    return "\n".join(lines)


def current_issue_body(issue):
    sub = ("<br />\n              " + issue["subtitle"]) if issue["subtitle"] else ""
    return """<h2>Current Issue</h2>
            <h3><a href="{d}/contents.htm">{label}{sub}</a></h3>
            <h5>Published: {published}</h5>
            <p>The authors, titles and keywords of papers published in this issue are listed below with the title linked to each paper in PDF format. These papers are hosted by CRISiSLab and download directly from this site.</p>
            <p>A full listing of this issue's papers including abstracts can be found in the <strong><a href="{d}/contents.htm">Contents Pages</a>.</strong></p>
            <hr width="70%" />
            <p>&nbsp;</p>
{downloads}
{papers}
            <p>&nbsp;</p>
            <p><img src="../images/velikalinija.png" alt="" class="line" border="0"/>
            </p>
            <p align="center">All papers are protected under the Creative Commons attribution as per our <a href="../info/copyright.htm">copyright notice</a>.</p>
        	<div style="clear:both;"></div>""".format(
        d=issue["dir"], label=issue["label"], sub=sub, published=issue["published"],
        downloads=downloads_block(issue, issue["dir"] + "/"),
        papers=paper_listing(issue, issue["dir"] + "/"))


def contents_body(issue):
    sub = ("<br />\n              " + issue["subtitle"]) if issue["subtitle"] else ""
    return """<h2>{label}</h2>
            <h3>Contents - {label}{sub}</h3>
            <h5>Published {published}</h5>
{downloads}
            <blockquote>&nbsp;</blockquote>
{papers}
            <p>&nbsp;</p>
            <p><img src="../../images/velikalinija.png" alt="" class="line" border="0"/></p>
            <p align="center">All papers are protected under the Creative Commons attribution as per our <a href="../../info/copyright.htm">copyright notice</a>.</p>
        	<div style="clear:both;"></div>""".format(
        label=issue["label"], sub=sub, published=issue["published"],
        downloads=downloads_block(issue, ""), papers=paper_listing_with_abstracts(issue, ""))


MAINBODY = re.compile(r'(<div id="mainbody">\s*).*?(\s*</div><!--main-->)', re.S)


def replace_mainbody(markup, body):
    if not MAINBODY.search(markup):
        raise SystemExit("could not find #mainbody block")
    return MAINBODY.sub(lambda m: m.group(1) + body + m.group(2), markup, count=1)


SIDEBAR = re.compile(r'(<div id="sidebar">\s*).*?(\s*</div>\s*<!--sidebar-->)', re.S)


def home_sidebar(issue):
    return """<subheading>
        	  Latest News
        	</subheading>
   	      <h3>Latest issue: Published {published}</h3>
   	      <p><a href="issues/current.html">{label}</a></p>
   	      <p>The newest issue of <em>AJDTS</em>, published by CRISiSLab following the
   	      archiving of the journal&rsquo;s Massey University website. It includes research on
   	      post-earthquake treatment seeking in Canterbury, climate change education in
   	      Vanuatu, and children&rsquo;s experiences of the 2019/2020 South Australian bushfires.
   	      <a href="issues/current.html">Download the papers</a>.</p>
            <p><img src="images/linija.png" alt="" class="line" border="0" /></p>
            <p>&nbsp;</p>
            <p><a href="issues/previous.html#Vol28-1">Volume 28, Number 1</a><br />
            A special issue in tribute to <em>Australasian Journal of Disaster and Trauma
            Studies</em> founder Professor Douglas Paton, with a focus on community resilience
            and disaster risk reduction. Hosted on the archived Massey site.</p>
            <p>&nbsp;</p>""".format(published=issue["published"], label=issue["label"])


# --------------------------------------------------------------------------
# Previous Issues: Volume 28 moves out of "current" and into the archive list
# --------------------------------------------------------------------------

VOL28_ROW = """              <tr>
                <td><strong>2024</strong></td>
                <td><a href="previous.html#Vol28-1">Volume 28, Number 1</a><br />
                Special Issue: A tribute to Professor Douglas Paton</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
"""

ROW_2023 = """              <tr>
                <td><strong>2023</strong></td>"""

ORIG_CURRENT_BODY = re.compile(r'<div id="mainbody">\s*<h2>Current Issues</h2>\s*(.*?)\s*<div style="clear:both;"></div>\s*</div><!--main-->', re.S)


def vol28_section(original_current):
    m = ORIG_CURRENT_BODY.search(original_current)
    if not m:
        raise SystemExit("could not lift the Volume 28 listing out of the original current.html")
    body = m.group(1)
    # the other year sections on this page do not repeat the copyright line
    body = re.sub(r'\s*<p align="center">All papers are protected.*?</p>', "", body, flags=re.S)
    return """            <div id="2024">
              <h3>2024 - Volume 28</h3>
			  <div id="Vol28-1">
%s
			  </div>
            </div>
""" % body


# --------------------------------------------------------------------------

OVERRIDE_CSS = """/* CRISiSLab overrides for the archived AJDTS stylesheet.
   The original site is a fixed 938px layout that floats on a background image
   carrying the Massey masthead. This trims the dead space below the footer so
   the page sits comfortably inside an embedded frame on crisislab.org.nz, and
   styles the hosting notice. */

#content {
	margin: 120px 0 40px 0;   /* 120px top keeps the Massey masthead in the
	                             background image visible, as on the original */
}

#wrapper {
	max-width: 938px;
}

#crisislab-notice {
	background: #eef4f9;
	border: 1px solid #c3d6e5;
	border-left: 4px solid #004B8D;
	margin: 0 0 12px 0;
	padding: 12px 18px;
}

#crisislab-notice p {
	font-size: 12px;
	line-height: 17px;
	color: #3d4b57;
	margin: 0;
	padding: 0;
}

#crisislab-notice strong {
	color: #004B8D;
}

#crisislab-notice a {
	color: #005AB2;
}

/* The archived stylesheet gives PDF links no affordance; flag the papers served
   from here as downloads. */
#mainbody h5 a.pdf:after {
	content: " (PDF)";
	font-size: 11px;
	font-weight: normal;
	color: #6b7b88;
	white-space: nowrap;
}
"""

ROBOTS = "User-agent: *\nAllow: /\n"


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    shutil.copytree(ORIGINAL, SITE)

    # PDFs for the issues we host ourselves
    for issue in ISSUES:
        src = os.path.join(NEW_ISSUE, issue["dir"])
        dst = os.path.join(SITE, "issues", issue["dir"])
        if not os.path.isdir(src):
            raise SystemExit("missing PDFs for issue %s (expected %s)" % (issue["dir"], src))
        shutil.copytree(src, dst)

    original_current = open(os.path.join(ORIGINAL, "issues", "current.html"), encoding="utf-8").read()

    # --- Current Issue -> the newest CRISiSLab-hosted issue
    page = os.path.join(SITE, "issues", "current.html")
    markup = replace_mainbody(original_current, current_issue_body(CURRENT))
    markup = markup.replace("<title>AJDTS - Current Issue</title>",
                            "<title>AJDTS - Current Issue</title>")
    open(page, "w", encoding="utf-8").write(markup)

    # --- Contents page for each hosted issue, built from the level-3 template
    for issue in ISSUES:
        tpl = original_current
        tpl = tpl.replace('href="../style.css"', 'href="../../style.css"')
        tpl = tpl.replace('src="../images/', 'src="../../images/')
        tpl = tpl.replace('href="../index.html"', 'href="../../index.html"')
        tpl = tpl.replace('href="../info/', 'href="../../info/')
        tpl = tpl.replace('href="../links/', 'href="../../links/')
        tpl = tpl.replace('href="current.html"', 'href="../current.html"')
        tpl = tpl.replace('href="previous.html"', 'href="../previous.html"')
        tpl = re.sub(r'<title>[^<]*</title>',
                     '<title>AJDTS - %s Contents</title>' % issue["label"], tpl, count=1)
        out = replace_mainbody(tpl, contents_body(issue))
        open(os.path.join(SITE, "issues", issue["dir"], "contents.htm"), "w", encoding="utf-8").write(out)

    # --- Home page sidebar
    page = os.path.join(SITE, "index.html")
    markup = open(page, encoding="utf-8").read()
    if not SIDEBAR.search(markup):
        raise SystemExit("could not find #sidebar block")
    markup = SIDEBAR.sub(lambda m: m.group(1) + home_sidebar(CURRENT) + m.group(2), markup, count=1)
    open(page, "w", encoding="utf-8").write(markup)

    # --- Previous Issues gains Volume 28
    page = os.path.join(SITE, "issues", "previous.html")
    markup = open(page, encoding="utf-8").read()
    if ROW_2023 not in markup:
        raise SystemExit("could not find the 2023 row in the previous-issues index")
    markup = markup.replace(ROW_2023, VOL28_ROW + ROW_2023, 1)
    markup = markup.replace('            <div id="2023">', vol28_section(original_current) + '            <div id="2023">', 1)
    open(page, "w", encoding="utf-8").write(markup)

    # --- Rewrite links and add chrome everywhere
    pages = HTML_PAGES + ["issues/%s/contents.htm" % i["dir"] for i in ISSUES]
    for page in pages:
        full = os.path.join(SITE, page)
        markup = open(full, encoding="utf-8").read()
        markup = rewrite_urls(markup, page)
        markup = add_chrome(markup, page)
        markup = open_external_in_new_tab(markup)
        open(full, "w", encoding="utf-8").write(markup)

    open(os.path.join(SITE, "crisislab.css"), "w", encoding="utf-8").write(OVERRIDE_CSS)
    open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8").write(ROBOTS)
    # GitHub Pages runs Jekyll unless told otherwise, which would skip any file
    # or directory beginning with an underscore.
    open(os.path.join(SITE, ".nojekyll"), "w", encoding="utf-8").write("")

    files = sum(len(f) for _, _, f in os.walk(SITE))
    print("built site/ — %d files, %d page(s) rewritten" % (files, len(pages)))


if __name__ == "__main__":
    main()
