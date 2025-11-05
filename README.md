# CheatingDL - Production notes

This repository contains a small Flask file-share app. A few production-oriented changes were made so the app can be safer and accept requests from your Netlify-hosted frontend domain.

What I changed
- Enabled CORS using `flask-cors` and allowed origins via the `ALLOWED_ORIGINS` environment variable.
- Read `SECRET_KEY` from the `SECRET_KEY` environment variable (falls back to the current value if not set).
- Replaced the permissive `allowed_file` implementation with an extension whitelist check.
- Added a `netlify.toml` file with a basic redirect rule (useful for SPAs / static hosting).
- Added `flask-cors` to `requirements.txt`.

Important notes about hosting on Netlify
- Netlify is a static-hosting platform. It does not run persistent Python web servers. If you want the full Flask backend accessible from the internet, deploy it to a Python-capable host (Render, Railway, Fly, Heroku, Azure Web App, etc.).
- If your frontend is hosted on Netlify at `https://localhostnotebook.netlify.app`, point your frontend API calls to the backend host URL and set `ALLOWED_ORIGINS` to include `https://localhostnotebook.netlify.app`.

Environment variables to set on your production host
- `SECRET_KEY` - A strong secret for Flask sessions and flash messages.
- `ALLOWED_ORIGINS` - Comma-separated origins allowed for CORS. Example:

  "https://localhostnotebook.netlify.app,https://your-other-front.example.com"

How to run locally (development)
1. Create a virtualenv and install requirements:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
$env:SECRET_KEY = 'dev-secret'; $env:ALLOWED_ORIGINS='http://localhost:5173,http://localhost:8080'; python main.py
```

3. Open `http://localhost:8080`.

If you want, I can:
- Add deployment instructions for a specific Python host (Render / Railway / Azure) and create a simple `Dockerfile` or `Procfile` for it.
- Move `templates/index.html` to a `public/` root and produce a Netlify-ready static front-end if you only want to host the UI on Netlify.

Next steps I recommend
1. Decide where to run the Flask backend (Render/Railway/Fly/etc.). I can add a `Dockerfile` and deployment steps.
2. On the frontend deployed to Netlify, ensure your API requests target the backend URL and not `localhost`.
3. Set production env vars on the backend host: `SECRET_KEY` and `ALLOWED_ORIGINS`.

