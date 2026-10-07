# AJDTS — CRISiSLab-hosted mirror

A rebuild of the *Australasian Journal of Disaster and Trauma Studies* website
(`psychlab.massey.ac.nz/trauma`, now archived by Massey) so that **Volume 29,
Number 1 (March 2026)** can be published and downloaded from crisislab.org.nz.

The split is deliberate:

| Content | Served from |
|---|---|
| Volume 29, Number 1 — complete issue + 3 papers | **here** (`issues/29-1/`) |
| Everything up to Volume 28, Number 1 | the archived Massey server, linked absolutely, opening in a new tab |
| Site chrome, About, Submissions, Editorial Board, Contact, Copyright, Web Links | **here** |

390 links point back at the archive. All 390 were checked and returned HTTP 200
on 6 October 2026.

## Layout

```
original/     pristine mirror of the Massey site — never edited, the build input
new-issue/    PDFs for issues CRISiSLab hosts itself, one folder per issue
issues.py     metadata (titles, authors, keywords, abstracts) for those issues
build.py      generates site/ from the three above
site/         the deployable static site — 44 files, 5.6 MB. Do not hand-edit.
```

Rebuild with:

```sh
python3 build.py
```

`build.py` is destructive on `site/` — it deletes and regenerates it every run,
so every change belongs in `original/`, `new-issue/`, or `issues.py`.

### Preview locally

```sh
python3 -m http.server 8899 --directory site
# then open http://127.0.0.1:8899/
```

## Publishing the next issue

1. Drop the PDFs into `new-issue/<dir>/`, e.g. `new-issue/29-2/`.
2. Add an entry at the **top** of `ISSUES` in `issues.py` (newest first). The
   first entry becomes the Current Issue; the ones below it are listed as
   previous issues.
3. Bump `UPDATED` in `issues.py` — it is the date stamped into every footer.
   It is pinned rather than taken from the build clock so that rebuilds are
   byte-for-byte reproducible, which is what lets CI check `site/` is current.
4. `python3 build.py`
5. Commit `site/` along with your changes and push.

The outgoing current issue does not need moving by hand — it falls into the
previous-issues list automatically.

## What was changed from the original

Everything below is done by `build.py`, so it survives a rebuild:

- **Link rewriting.** Every link to content that stayed on the archive became an
  absolute `psychlab.massey.ac.nz` URL with `target="_blank"`, so it escapes the
  Wix frame instead of loading inside it.
- **Current Issue** now shows Volume 29, Number 1, with a contents page at
  `issues/29-1/contents.htm` carrying the full abstracts.
- **Previous Issues** gained a 2024 row and a Volume 28 section, lifted from the
  original Current Issue page.
- **Home page** sidebar now leads with Volume 29.
- **Hosting credit** in the footer only — "Hosted by CRISiSLab", with the
  domain linking to the archived Massey site. There is deliberately no banner
  on the pages: the journal should read as the journal.
- **Search box** repaired. The original posted to `google.com/custom` with a
  sitesearch for `www.massey.ac.nz/~trauma`, a domain that has 404'd for years.
  It now runs a Google `site:` search against the archive.
- **Footer** credits CRISiSLab as host, links the domain to the archive, and
  restamps the "Updated" date at build time.
- **Two broken links in the original** were repaired: `info/copyright.html`
  (the file is `copyright.htm`) and a commented-out `contact.html` that never
  existed beside the pages referencing it.
- **Made responsive.** The original is a 938px fixed design from about 2012
  with no viewport meta, so a phone rendered it at 980px and zoomed out to a
  postage stamp. `build.py` now injects
  `<meta name="viewport" content="width=device-width, initial-scale=1">` into
  every page and `crisislab.css` adds the media queries. See below.
- **`crisislab.css`** — a small override layer. The original stylesheet is
  untouched.

### The responsive layer

Three breakpoints, all in `OVERRIDE_CSS` in `build.py`:

| Width | What changes |
|---|---|
| **≤ 938px** (the design width) | Layout goes fluid; the menu wraps and the search box takes its own row; long bare URLs on the Web Links page break instead of pushing the page sideways |
| **≤ 760px** | The home page's sidebar and article stack; the heading boxes rejoin the flow; body copy goes to 14px/1.55 |
| **≤ 560px** | The year/volume index and the editorial board stack into lists; the masthead stops shrinking |

Three things in the original fought back and are worth knowing about:

- **The masthead is a background image.** `images/background-ajdts.jpg` is
  1694px wide and the Massey logo and the Ruapehu photo are positioned for a
  938px band cropped out of its centre — the page just leaves 120px of margin
  above itself to let them show. Left alone, a phone crops that band to the
  middle 375px and the Massey logo disappears. Below 938px the image is scaled
  to 180.6% of the viewport (1694/938) so the band always matches the page
  width, with the top margin scaled to match at 12.8% (120/938). Below 560px
  even that makes the logo illegible, so the image is pinned at 1186px and
  anchored at `30% top`: the logo stays readable top left and the photo crops
  off the right instead.
- **The headings are absolutely positioned.** `h2` and `#mainbody h2` are boxes
  with negative margins that hang up and left out of the content, and
  `#mainbody h2` is `white-space: nowrap` on top of that. In a fluid column
  they either overflow the page or land on the text, so below 760px they go
  back to `position: static` and are allowed to wrap.
- **Layout tables are padded with `&nbsp;` cells.** Invisible as table cells,
  but blank lines once the table is stacked. `mark_filler_cells()` tags them
  `class="empty"` at build time so the stacked view can drop them.

Nothing above 938px changed: the embed is 980px wide, so the Wix desktop view
renders exactly as it did before.

## Deployment

Hosted on **GitHub Pages** from `crisislab-platform/ajdts`.
`.github/workflows/pages.yml` publishes `site/` on every push to `main`, and
first re-runs `build.py` to fail the build if `site/` was not regenerated after
a source change.

`site/` is committed rather than built fresh in CI on purpose: it makes the
deployed bytes reviewable in a diff, and it means the site can be served from
any static host by copying one folder.

Nothing in the site is root-absolute, so it works under a subpath
(`/ajdts/`) as well as at a domain root — useful if `ajdts.crisislab.org.nz`
is CNAME'd to it later.

## Embedding in the Wix site

Live at **https://crisislab-platform.github.io/ajdts/** and embedded in the Wix
site on a page called **AJDTS Journal**, as an *Embed a site* (iframe)
component:

| Setting | Value |
|---|---|
| URL | `https://crisislab-platform.github.io/ajdts/` |
| Component size | 980 x 1163 px, at X 0, Y 0 |
| Containing section | 980 x 1320 px |
| Alt text | Australasian Journal of Disaster and Trauma Studies |

Two things that are easy to get wrong when editing this:

- **The section must stay taller than the component.** The section defaulted to
  500px while the component was 1163px, and the site footer rendered on top of
  the bottom of the embed. The 157px of slack is what keeps them apart.
- **Clicking the embed in the editor selects the section, not the component** —
  the iframe swallows the click. Select it via the *Layers* panel instead
  (Section: Untitled -> HTML).

### The mobile layout of the embed is set separately, and is still wrong

Wix keeps a second set of coordinates for the mobile view, and the embed never
got one. Checked on 7 October 2026 by fetching
`https://www.crisislab.org.nz/ajdts-journal` with an iPhone user agent and
reading the server-rendered CSS:

```
#comp-muvy1ext { width: 280px; height: 332px; }     /* the embed   */
#comp-muvy06ww { width: 320px; }                    /* its section */
```

280px wide is fine — the site is responsive down to 280 — but **332px tall is
not**. The journal home page is 2036px tall at that width, so a phone gets the
whole site inside a 332px letterbox that scrolls internally. That is what makes
the page feel broken on a phone, and no amount of CSS inside the iframe can fix
it: the height is the host page's decision.

It has to be set by hand in the Wix editor's **mobile view** (the phone icon in
the top bar), selecting the component via *Layers*:

| | Now | Should be |
|---|---|---|
| Component | 280 x 332 at X 20 | 320 x 1860 at X 0 |
| Section | 320 x ~390 | 320 x 1960 |

1860px is the home page's height at 320px wide, measured in a 320px frame, the
same way the desktop 1163px was chosen. Keep the section taller than the
component or the site footer renders over the bottom of the embed, exactly as
it did on desktop. Deeper pages (Current Issue, and especially the Previous
Issues index at ~77,000px) still scroll inside the frame, which is the same
trade the desktop embed makes.

### PDF links download rather than open

The Volume 29 links carry `download target="_blank" rel="noopener"`, so clicking
one saves the file instead of rendering it in the browser's PDF viewer — which,
inside the Wix embed, would otherwise display the paper in the iframe.

GitHub Pages cannot send `Content-Disposition: attachment` (it supports no
custom headers), so this is done client-side with the HTML `download`
attribute. That attribute is only honoured for **same-origin** URLs, which is
why it applies to the issues we host but is silently ignored on the links back
to the Massey archive — those open in a new tab instead, which is the most that
can be done for a file on someone else's server.

`target="_blank"` is the fallback: if a sandboxed frame ever blocks the
download, the PDF opens in its own tab rather than inside the embed.

If a true `Content-Disposition` header is ever wanted, that means moving off
GitHub Pages — Cloudflare Pages and Netlify both support a `_headers` file.

### Downloads must live outside the embed

Wix renders the embed inside a sandboxed iframe:

```
sandbox="allow-same-origin allow-forms allow-popups
         allow-modals allow-scripts allow-pointer-lock"
```

`allow-downloads`, `allow-top-navigation` and `allow-popups-to-escape-sandbox`
are all absent, so **nothing inside the embed can trigger a download** — not the
`download` attribute, not a server `Content-Disposition`, and not via a new tab
(popups inherit the sandbox). Clicking a paper inside the embed opens it in the
browser's PDF viewer, and that cannot be changed from this side.

So the Volume 29 PDFs were also imported into the site's Wix Media Manager, and
the download links belong on the Wix page itself, above the embed. Wix forces a
download when `?dn=<filename>` is appended:

| Paper | URL |
|---|---|
| Complete issue | `https://www.crisislab.org.nz/_files/ugd/c74a14_0f84bfcbe093446ca8d546fb79634a6a.pdf?dn=AJDTS_29_1_full.pdf` |
| Woods et al. | `https://www.crisislab.org.nz/_files/ugd/c74a14_9b5f0a6a11274ae09327ae00a1bbeecf.pdf?dn=AJDTS_29_1_Woods.pdf` |
| Pierce | `https://www.crisislab.org.nz/_files/ugd/c74a14_7ee7554fe9a14d4fb4ff9ab4df5d32bd.pdf?dn=AJDTS_29_1_Pierce.pdf` |
| Lycos et al. | `https://www.crisislab.org.nz/_files/ugd/c74a14_5eeea131b1b147ef8e3f25629d1d9d5b.pdf?dn=AJDTS_29_1_Lycos.pdf` |

All four verified returning `content-disposition: attachment` with byte-exact
sizes. Without `?dn=` the same URLs open in the viewer instead.

Note this means each paper now exists twice: in this repo (served by GitHub
Pages, inside the embed) and in Wix Media Manager (for the download links). A
corrected paper has to be replaced in both. Re-import to Wix with:

```
POST https://www.wixapis.com/site-media/v1/files/import
{"url": "<public URL>", "displayName": "...", "mimeType": "application/pdf",
 "mediaType": "DOCUMENT", "private": false}
```

### Why the height is fixed — and why it need not be

Every page posts its scroll height to the parent (`{ ajdtsHeight: ... }`, see
`EMBED_JS` in build.py), so a Velo `onMessage` handler could resize the
component to fit each page. That was not wired up, on the understanding that
the classic Editor positions elements absolutely and does not reflow when a
component's height changes at runtime — a taller embed would slide under the
footer instead of pushing it down.

**That turns out not to be true of this page.** Measured on the live page on
7 October 2026: the section's grid container is `height: auto` with
`min-height: 1620px`, and its content is 166 + 1163 + 10 = 1339px, so it is
carrying 281px of slack. Growing `#comp-muvy1ext` from 1163px to 2400px
(+1237px) moved the footer down by exactly 1237 - 281 = **956px**, and the
document grew by the same 956px. The page reflows 1:1 once the slack is used
up. On mobile the same container has `min-height: auto`, so it would reflow
immediately.

So the Velo auto-resize is live-able, and it is the better fix: one handler and
the embed fits every page at every width, instead of a height that is only
right for the home page. Something like, in the page's Velo code:

```js
$w.onReady(() => {
  $w('#html1').onMessage((e) => {
    if (e.data && e.data.ajdtsHeight) {
      $w('#html1').height = e.data.ajdtsHeight + 20;
    }
  });
});
```

(`#html1` is whatever Velo names `comp-muvy1ext`; check it in Dev Mode. Clamp
it if you want — the Previous Issues index is ~77,000px tall on a phone.)

Until that is done the embed is a fixed 1163px on desktop and taller pages
scroll inside it. 1163px fits the journal's home page exactly, footer and all.

## Known issues

- **The complete-issue PDF has the wrong title metadata.** `AJDTS_29_1_full.pdf`
  carries `Volume 26, Number 1` in its PDF title field, left over from the
  InDesign template. Harmless on the web, but it is what shows in a PDF reader's
  title bar and what some reference managers pick up. Worth fixing at source.
- **The back catalogue depends on the archive staying up.** It is live today,
  but it has already been archived once. Mirroring all ~28 volumes here would be
  a few hundred megabytes and is the obvious next step if Massey signals the
  server is going away.
- `images/ajdts_footer-graphic.jpg` 404s on the original and is missing here
  too. It sits inside an HTML comment and never renders.
