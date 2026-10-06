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
site/         the deployable static site — 43 files, 5.6 MB. Do not hand-edit.
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
- **Hosting notice** on every page explaining the archive and naming CRISiSLab
  as the host.
- **Search box** repaired. The original posted to `google.com/custom` with a
  sitesearch for `www.massey.ac.nz/~trauma`, a domain that has 404'd for years.
  It now runs a Google `site:` search against the archive.
- **Footer** credits CRISiSLab as host, links the domain to the archive, and
  restamps the "Updated" date at build time.
- **Two broken links in the original** were repaired: `info/copyright.html`
  (the file is `copyright.htm`) and a commented-out `contact.html` that never
  existed beside the pages referencing it.
- **`crisislab.css`** — a small override layer. The original stylesheet is
  untouched.

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

### Why the height is fixed

Every page posts its scroll height to the parent (`{ ajdtsHeight: ... }`, see
`EMBED_JS` in build.py), so a Velo `onMessage` handler could resize the
component to fit each page. That is deliberately **not** wired up: this is the
classic Wix Editor, where elements are absolutely positioned and the page does
not reflow when a component's height changes at runtime. Growing the component
would slide it under the footer rather than push the footer down.

So the embed is a fixed 1163px and taller pages scroll inside it. 1163px fits
the journal's home page exactly, footer and all. The Current Issue page and the
very long Previous Issues index scroll internally, which is normal behaviour for
an embedded site.

The postMessage is left in place because it costs nothing and becomes useful if
the site ever moves to Wix Studio, where sections do reflow.

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
