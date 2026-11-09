# CW News – web version

**Pomysł i autor: SP2Z**

News headlines sent in Morse code (CW), in the browser. Works on iPhone, Android and computers. Web version of the CW News Android app.

## How it works
- `site/index.html` is the whole app: Morse encoding, audio synthesis, all settings and buttons.
- Browsers can't read news RSS feeds directly, so the GitHub Action `.github/workflows/deploy.yml` fetches all feeds every ~10 minutes (`scripts/fetch_feeds.py`), saves them as `feeds.json` and publishes the site on GitHub Pages.

## Using it on iPhone
Open the page in **Safari** → Share → **Add to Home Screen**. Tap **Start**.
Lock-screen controls: ⏭ = Skip, ⏮ = back 1 word.

## Note
GitHub pauses scheduled workflows in public repos after 60 days without commits. If headlines stop updating, open **Actions → Fetch news and deploy → Enable workflow**, or push any small change.
