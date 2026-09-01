# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```

### Deploy publicly

This repository is now ready for public hosting with both the Streamlit UI and the city-ledger backend:

- The Streamlit frontend runs from streamlit_app.py.
- The backend API runs from backend.py and serves /health and /city-ledger.
- A requirements file is included for hosted installs.
- A runtime file is included for Python 3.11.

For Streamlit Community Cloud:
1. Push this repository to GitHub.
2. Open Streamlit Community Cloud and create a new app.
3. Point it at this repo and select streamlit_app.py as the app file.

For a backend-style deployment (Render, Railway, Fly.io, or similar):
1. Use backend.py as the start command.
2. Set the PORT environment variable.
3. The service will expose /health and /city-ledger.
