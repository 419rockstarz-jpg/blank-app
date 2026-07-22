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

This repository is now set up to be deployed to Streamlit Community Cloud or similar platforms:

- The app entrypoint is the existing Streamlit file.
- A requirements file is included for hosted installs.
- A runtime file is included for Python 3.11.

If you push this repository to GitHub, you can deploy it from Streamlit Community Cloud by pointing it at the repo and selecting the app file.
