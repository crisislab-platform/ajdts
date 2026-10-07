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
# chrome: stylesheet, working search box, footer credit
# --------------------------------------------------------------------------

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

# The original predates responsive design and carries no viewport meta, so a
# phone renders it at 980px and zooms out. crisislab.css does the rest.
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1" />'

# The year/volume index and the editorial board are laid out with tables padded
# out by &nbsp; cells. Those cells are invisible as table cells but become
# blank lines once crisislab.css stacks the table on a narrow screen, so tag
# them to be hidden there.
FILLER_CELL = re.compile(r'<td([^>]*)>(\s*&nbsp;\s*)</td>', re.I)


def mark_filler_cells(markup):
    return FILLER_CELL.sub(
        lambda m: '<td class="empty"%s>%s</td>' % (m.group(1), m.group(2)), markup)


def add_chrome(markup, page):
    up = "../" * page.count("/")
    markup = markup.replace("<head>", "<head>\n" + VIEWPORT, 1)
    markup = STYLE_LINK.sub(
        lambda m: m.group(0) + '\n<link rel="stylesheet" type="text/css" href="%scrisislab.css" />' % up,
        markup, count=1)
    markup = SEARCH_FORM.sub(lambda m: NEW_SEARCH_FORM, markup, count=1)
    markup = fix_footer(markup)
    markup = mark_filler_cells(markup)
    markup = markup.replace("</body>", EMBED_JS + "</body>", 1)
    return markup


# --------------------------------------------------------------------------
# page content for the issues we host
# --------------------------------------------------------------------------

# The PDFs we host should save to disk, not open in the browser's built-in
# viewer — in the Wix embed that would otherwise render inside the iframe.
# GitHub Pages cannot set Content-Disposition, but `download` does the same job
# client-side and is honoured because these files are same-origin. target
# _blank is the fallback: if a sandboxed frame blocks the download, the PDF
# opens in its own tab instead of inside the embed.
DOWNLOAD_ATTRS = ' download target="_blank" rel="noopener"'


def paper_listing(issue, prefix):
    """Author/title/keyword listing, as used on the Current Issue page."""
    out = []
    for section in issue["sections"]:
        out.append('            <h4>%s</h4>' % section["heading"])
        for p in section["papers"]:
            out.append('            <h5><a class="pdf" href="%s%s"%s>%s</a></h5>'
                       % (prefix, p["pdf"], DOWNLOAD_ATTRS, p["title"]))
            out.append('            <p><em>%s</em></p>' % p["authors"])
            out.append('            <p><strong>Keywords: </strong>%s</p>' % p["keywords"])
    return "\n".join(out)


def paper_listing_with_abstracts(issue, prefix):
    out = []
    for section in issue["sections"]:
        out.append('            <h4>%s</h4>' % section["heading"])
        for p in section["papers"]:
            out.append('            <h5><a class="pdf" href="%s%s"%s>%s</a></h5>'
                       % (prefix, p["pdf"], DOWNLOAD_ATTRS, p["title"]))
            out.append('            <p><em>%s</em></p>' % p["authors"])
            out.append('            <p><strong>Keywords: </strong>%s</p>' % p["keywords"])
            out.append('            <blockquote>')
            out.append('              <p><strong>Abstract</strong>:<br />')
            out.append('              %s</p>' % p["abstract"])
            out.append('            </blockquote>')
    return "\n".join(out)


def downloads_block(issue, prefix):
    lines = ['            <h5><a href="%s%s"%s>%s</a> (complete issue, PDF)</h5>'
             % (prefix, issue["full_pdf"], DOWNLOAD_ATTRS, issue["label"])]
    if issue.get("contents_pdf"):
        lines.append('            <p><a href="%s%s"%s>Contents page - %s</a></p>'
                     % (prefix, issue["contents_pdf"], DOWNLOAD_ATTRS, issue["label"]))
    return "\n".join(lines)


def current_issue_body(issue):
    sub = ("<br />\n              " + issue["subtitle"]) if issue["subtitle"] else ""
    return """<h2>Current Issue</h2>
            <h3><a href="{d}/contents.htm">{label}{sub}</a></h3>
            <h5>Published: {published}</h5>
            <p>The authors, titles and keywords of papers published in this issue are listed below with the title linked to each paper in PDF format.</p>
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
   	      <p>This issue includes research on treatment seeking in the years after the
   	      Canterbury earthquake sequence, climate change education in Vanuatu, and
   	      children&rsquo;s experiences of the 2019/2020 South Australian bushfires.
   	      <a href="issues/current.html">Download the papers</a>.</p>
            <p><img src="images/linija.png" alt="" class="line" border="0" /></p>
            <p>&nbsp;</p>
            <p><a href="issues/previous.html#Vol28-1">Volume 28, Number 1</a><br />
            A special issue in tribute to <em>Australasian Journal of Disaster and Trauma
            Studies</em> founder Professor Douglas Paton, with a focus on community resilience
            and disaster risk reduction.</p>
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
   adds the responsive layer the original never had. */

html {
	-webkit-text-size-adjust: 100%;
	text-size-adjust: 100%;
}

#content {
	margin: 120px 0 40px 0;   /* 120px top keeps the Massey masthead in the
	                             background image visible, as on the original */
}

#wrapper {
	width: auto;
	max-width: 938px;         /* the design width; fluid below it */
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

/* =====================================================================
   Responsive layer

   The original is a 938px fixed design from ~2012: no viewport meta, two
   floated columns, headings positioned absolutely so their boxes hang out
   over the content, and a 1694px background image whose only job is to put
   the Massey masthead above the page. None of it survives a phone, so:

     <= 938px   the layout goes fluid and the background scales with it
     <= 760px   the two columns stack and the heading boxes rejoin the flow
     <= 560px   index tables stack into lists
   ===================================================================== */

img {
	max-width: 100%;
	height: auto;
}

@media (max-width: 938px) {
	/* the 0.4em the reset hands every element, including these two */
	html, body { margin: 0; }

	/* The masthead lives in the background image: the Massey logo and the
	   Ruapehu photo are placed for a 938px band cropped out of a 1694px
	   image (938/1694 = 55.4%, hence 180.6%). Scaling the image to that
	   same ratio of the viewport keeps both in the same place at any width,
	   and 12.8% (120/938) keeps the content box under them. */
	body { background-size: 180.6% auto; }

	#content {
		width: auto;
		margin: 12.8% 0 24px 0;
		padding: 10px;
	}

	#mainbody {
		width: auto;
		float: none;
		padding: 35px 18px 25px 18px;
	}

	#mainbody img.line { padding-left: 0; }   /* was indented 155px */

	table { max-width: 100%; }

	/* The Web Links page prints bare URLs as text and several are wider than
	   a phone, which pushes the whole page sideways. */
	#main, #mainbody, #sidebar, td, th { overflow-wrap: break-word; }

	#header { padding: 12px 10px; }

	/* The menu runs out of room at exactly the design width, so from here
	   down let the items wrap over as many rows as they need and give the
	   search box its own row instead of squeezing it onto the end. */
	#menu ul { padding: 2px 4px; }
	#menu ul li { display: inline-block; }
	#menu ul li a { padding: 9px 6px; }

	/* the search sits in the last <li>; give it a row to itself */
	#menu ul li:has(#searchform) { display: block; }

	/* The submit button is positioned against .fieldcontainer, so the width
	   cap belongs there rather than on the input. */
	#searchform,
	#searchform .fieldcontainer {
		display: block;
		width: auto;
		max-width: 320px;
		margin: 4px 2px 6px 2px;
	}

	.searchfield,
	.searchfield:focus {
		width: 100%;
		font-size: 16px;          /* under 16px iOS zooms the page on focus */
		padding: 7px 32px 7px 7px;
	}

	#searchbtn {
		top: 50%;
		right: 5px;
		margin-top: -12px;
	}
}

@media (max-width: 760px) {
	h1 {
		font-size: 24px;
		line-height: 1.15;
	}

	/* Home page: sidebar above the article instead of beside it. */
	#sidebar {
		width: auto;
		float: none;
		background-image: none;   /* the vertical rule between the columns */
		border-bottom: 3px solid #e5edf3;
		padding: 8px 10px 12px 10px;
	}

	#sidebar subheading {
		display: inline-block;
		width: auto;
	}

	#main {
		margin: 0;
		padding: 14px 10px 20px 10px;
	}

	#mainbody { padding: 14px 12px 20px 12px; }

	/* The heading boxes are absolutely positioned with negative margins so
	   they overhang the content above them. In a fluid column that either
	   overflows the page or lands on top of the text, so put them back in
	   the flow and let them wrap. */
	h2,
	#mainbody h2 {
		position: static;
		width: auto;
		height: auto;
		margin: 0 0 14px 0;
		padding: 11px 14px;
		background-image: linear-gradient(180deg, rgba(229,237,243,1) 0%, rgba(76,129,175,0.5) 100%);
		background-repeat: no-repeat;
		background-size: 100% 100%;
		font-size: 21px;
		line-height: 1.2;
		white-space: normal;
		color: #004B8D;
	}

	/* The original sets line-height equal to font-size, which is unreadable
	   on a phone-width measure. */
	#main p,
	#mainbody p,
	#sidebar p,
	#mainbody li,
	#mainbody dd,
	#mainbody dt {
		font-size: 14px;
		line-height: 1.55;
	}

	#main blockquote,
	#mainbody blockquote {
		font-size: 14px;
		line-height: 1.5;
		text-align: left;         /* justified text rivers at this measure */
		margin-left: 0;
		margin-right: 0;
	}

	#mainbody h5 { line-height: 1.35; }
	#mainbody h4 { padding-left: 0; }
	h3 { line-height: 1.3; }

	/* Thumbnail strip: fluid, with the two arrows parked on the right. */
	#slider { text-align: left; }

	.scrollable {
		width: calc(100% - 46px);
		float: left;
	}

	a.browse,
	a.left,
	a.right {
		left: auto;
		right: 0;
		margin: 40px 4px;
	}

	/* Footer: let the three credits and the menu wrap instead of fighting
	   each other across one line. */
	#footer { text-align: left; }

	#footer span,
	#footer date {
		float: none;
		display: inline-block;
	}

	#footer date { padding: 0 10px 0 0; }
	#footer ul { padding: 4px 0 0 0; }
	#footer ul li a { padding: 0 5px 0 0; }
}

@media (max-width: 560px) {
	/* Below this the proportional masthead above shrinks the Massey logo to
	   about 100px and it stops being readable. Pin the image at a size that
	   keeps the logo legible, anchored so the logo sits top left, and let
	   the Ruapehu photo crop off the right edge instead. */
	body {
		background-size: 1186px auto;
		background-position: 30% top;
	}

	#content { margin-top: 84px; }

	h1 { font-size: 20px; }

	h2,
	#mainbody h2 { font-size: 19px; }

	/* The year/volume index and the editorial board are layout tables. Stack
	   them into lists; build.py tags the filler cells so they can go. */
	#mainbody table,
	#mainbody tbody,
	#mainbody tr,
	#mainbody td {
		display: block;
		width: auto;
	}

	#mainbody tr {
		padding: 4px 0 8px 0;
		border-bottom: 1px solid #dfe6ec;
	}

	#mainbody td { padding: 2px 0; }
	#mainbody td.empty { display: none; }
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
