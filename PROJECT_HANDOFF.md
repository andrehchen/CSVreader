# CSV Explorer — Project Handoff

## What this is
A small Streamlit web app: upload any CSV, get an automatic profile, plain-English
insights, and charts. Built as a first "ship something end-to-end" project. The goal
is a live public URL, not a polished product.

## Why (context)
- Hands-on practice with building + deploying, to prep for hackathons.
- Target event: Hack the North (University of Waterloo, Sept 18–20, 2026). Hacker
  applications open mid-summer and historically close early-to-mid August — check
  apply.hackthenorth.com.
- A shipped repo + live URL also serves as portfolio evidence (the GitHub link that
  hackathon applications explicitly look for).

## Stack
- Python + Streamlit (pure Python, no JS / frontend framework)
- pandas + numpy for the analysis
- Deploy target: Streamlit Community Cloud (free, GitHub-connected)

## Files
- `app.py` — the entire app (~100 lines)
- `requirements.txt` — streamlit, pandas, numpy

## Current features (done)
- Overview metrics: rows, columns, missing cells; 50-row preview
- Column profile table: dtype, missing %, unique count per column
- Auto-insights, plain English: high-missingness columns, constant (no-info) columns,
  likely ID columns, skewed numeric columns, 3-SD outliers, and strongly correlated
  numeric pairs (|r| > 0.7)
- Histogram (20 bins) for a selected numeric column
- Correlation matrix + scatter plot

**Key implementation note:** the insights are assembled into a Python list of strings
named `insights`. That list is the hook for the AI feature below.

## Run locally
```
pip install streamlit pandas numpy
streamlit run app.py
```
Opens at localhost; upload a CSV. (Use `pip3` / `python -m streamlit run app.py` if the
plain commands aren't found.)

## Deploy (ship it)
Repo: https://github.com/andrehchen/CSVreader

First push — folder already contains `app.py` + `requirements.txt`, no git yet:
```
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/andrehchen/CSVreader.git
git push -u origin main
```
Auth note: GitHub rejects account passwords on push. Easiest fix is `gh auth login`
before pushing; alternatives are GitHub Desktop or a Personal Access Token
(github.com/settings/tokens) pasted as the password. Zero-git fallback: use GitHub's
"upload an existing file" button in the browser — deploys identically.

Then: share.streamlit.io → sign in with GitHub → New app → pick repo / `main` / `app.py`
→ Deploy → live URL.

## Next steps (prioritized)
1. **AI summary (v2 — the demo-worthy feature).** The `insights` list is already built.
   Join it into one string, send it to an LLM with a prompt like: "In two sentences,
   describe what this dataset is and its main data-quality issues." Display the reply at
   the top of the app.
   - Needs an API key in Streamlit secrets (`.streamlit/secrets.toml` locally; the
     Secrets UI on Streamlit Cloud). Do not commit the key.
   - Ship the non-AI version first; add this as v2.
2. Nice-to-haves: download button for the profile table; a slider/filter on a numeric
   column; datetime-column detection; a "top values" breakdown for categorical columns.

## Decisions / rationale (so nothing gets silently undone)
- Streamlit chosen so the coding stays trivial and the effort goes into deploying — the
  part that's actually a new skill.
- No matplotlib/seaborn: dependencies kept minimal to reduce deploy-failure risk. Uses
  native Streamlit charts + a numpy histogram instead.
- The histogram replaced an earlier `value_counts()` chart, which was broken for
  continuous data (spiky and uninformative).
