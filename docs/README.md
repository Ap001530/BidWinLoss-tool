# GitHub Pages site

`index.html` + `data/*.json` is a fully standalone version of the thesis dashboard
(same content as `dashboard/`, rebuilt to run outside the Claude Artifact host):
plain HTML/CSS/JS, `fetch()` for its data instead of the Artifact `dash` API, and
its own CSS tokens instead of the Artifact host's design-system variables. Verified
headlessly (jsdom) before committing: all sections render, the ROC curve draws, and
the scorer computes a live probability.

## Turning this on

GitHub Pages isn't enabled by pushing these files alone — it's a repo setting:

1. On GitHub, go to **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Branch: this branch (or `main`, after merging) · Folder: **/docs**.
4. Save. GitHub builds and gives you a URL like
   `https://ap001530.github.io/BidWinLoss-tool/` within a minute or two.

## Regenerating the data

```bash
python3 data/generate_synthetic_bids.py
python3 src/train_model.py          # writes outputs/model_results.json
python3 dashboard/make_tables.py    # writes dashboard/tables/*.json
cp dashboard/tables/*.json docs/data/
```

`index.html` itself only needs republishing if you change its layout or logic —
the data files are the part that changes when the pipeline is re-run.
