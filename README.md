# CodeAlpha URL Shortener

A URL shortener built with Python, Flask, MongoDB, HTML, CSS, and JavaScript.

## Features

- Create short links for HTTP/HTTPS URLs
- Store original URLs and short codes in MongoDB
- Redirect short links to their original destinations
- Reuse the existing short link when the same URL is submitted again
- Track redirect clicks
- Validate input and return useful API errors
- Responsive frontend with copy-link action

## Requirements

- Python 3.10+
- MongoDB running locally or a MongoDB Atlas connection string
- Git (for GitHub submission)

## Setup

1. Create and activate a virtual environment:

   **Windows (PowerShell)**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `MONGODB_URI`.

   For a local MongoDB instance, the default URI is:
   `mongodb://127.0.0.1:27017/`

   For MongoDB Atlas, use the connection string provided by Atlas. Keep credentials private and never commit `.env`.

4. Start the application:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## API endpoints

### `POST /api/shorten`

Request:
```json
{
  "url": "https://www.example.com/products"
}
```

Success response (`201 Created`):
```json
{
  "original_url": "https://www.example.com/products",
  "short_code": "Ab3xK9Q",
  "short_url": "http://127.0.0.1:5000/Ab3xK9Q",
  "message": "Short URL created successfully."
}
```

The short code and example URL above are illustrative; your app generates its own code.

### `GET /<short_code>`

Redirects to the original URL and increments its click counter.

### `GET /health`

Returns application/database health information.

## Test with curl

```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.example.com"}'
```

Then open the returned `short_url` in your browser.

## GitHub submission

Suggested repository name: `CodeAlpha_URLShortener`

```bash
git init
git add .
git commit -m "Build CodeAlpha URL shortener"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/CodeAlpha_URLShortener.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Do not commit `.env` or database credentials.

## Notes

- This is a learning/internship project, not a production-hardened public URL service.
- Before public deployment, add rate limiting, abuse/malware protections, HTTPS, logging/monitoring, and production server configuration.
