# Nassau Candy — product line profitability dashboard

Streamlit analytics for gross margin, division performance, cost diagnostics, and Pareto (profit concentration).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Keep `Nassau Candy Distributor (1).csv` in the same folder as `app.py` (default data path).

## Repository

GitHub: [https://github.com/Vaishu552003/nassau-candy-profitability](https://github.com/Vaishu552003/nassau-candy-profitability)

## Docs

- [Research paper](docs/Research_Paper.md)
- [Executive summary](docs/Executive_Summary.md)

## Deploy (Streamlit Community Cloud)

1. Open **[share.streamlit.io](https://share.streamlit.io)** and click **Sign in** (use the **same GitHub account** that owns this repo: `Vaishu552003`).
2. **Create app** (or **New app**):  
   - Repository: **`Vaishu552003/nassau-candy-profitability`**  
   - Branch: **`main`**  
   - Main file path: **`app.py`** (lowercase, in the repo root)
3. If GitHub asks for permissions, **install/authorize the Streamlit Cloud GitHub App** and allow access to this repository (and **all repositories** if the repo does not appear in the list).
4. Wait for the build to finish. Copy the app URL from the dashboard — it should look like **`https://<something>.streamlit.app`**.  
   **Do not** use `https://share.streamlit.io/errors/not_found` as your “deployed link”; that page only means the link was wrong or you are not signed in.

### If you see “You do not have access to this app or it does not exist”

| Cause | What to do |
|--------|------------|
| Not signed in | Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub, then open the app from **My apps**. |
| Wrong / old URL | Open **My apps** → select your app → use the **`.streamlit.app`** URL Streamlit shows. |
| App never deployed | Create the app again (steps above). First successful build must finish before the public URL works. |
| Repo not visible to Streamlit | GitHub → **Settings** → **Applications** → **Streamlit Cloud** → ensure this repo is allowed. |

This repo includes **`runtime.txt`** (`python-3.11`). In Streamlit Cloud you can also set Python under **Advanced settings** when you deploy.
