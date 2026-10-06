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

The site is a fixed 938px-wide layout, so the Wix page needs a content area at
least that wide.

1. In the Wix Editor: **Add → Embed Code → Embed a Site (iFrame)**, set the URL
   to wherever `site/` is deployed, and set the width to 940px.
2. Because Wix HTML components are a fixed height and the Previous Issues page
   is very tall, every page posts its height to the parent window. Velo is
   enabled on this site, so the page code can resize the component to fit:

```js
// Wix page code
$w.onReady(() => {
  $w('#html1').onMessage((event) => {
    if (event.data && event.data.ajdtsHeight) {
      $w('#html1').height = Math.min(event.data.ajdtsHeight, 20000);
    }
  });
});
```

Replace `#html1` with the component's actual ID. Without this the embed still
works — it just scrolls inside its own box.

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
