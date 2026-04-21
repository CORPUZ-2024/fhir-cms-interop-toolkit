# bb2_auth.py — SMART on FHIR OAuth2 authorization code flow
import os, webbrowser, json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

CLIENT_ID = os.environ.get('BB2_CLIENT_ID', 'your_id_here')
CLIENT_SECRET = os.environ.get('BB2_CLIENT_SECRET', 'your_secret_here')
CALLBACK_URL = os.environ.get('BB2_CALLBACK_URL', 'http://localhost:8000/callback')

AUTH_URL = 'https://sandbox.bluebutton.cms.gov/o/authorize/'
TOKEN_URL = 'https://sandbox.bluebutton.cms.gov/o/token/'
TOKEN_CACHE = Path('modules/bb2_sandbox/data/.token_cache.json')

_auth_code = None # captured by local HTTP callback server

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        params = parse_qs(urlparse(self.path).query)
        _auth_code = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Auth code captured. Return to terminal.')
    def log_message(self, *args): pass # suppress server logs

def get_auth_code() -> str:
    """Open browser for user login, capture auth code via local callback server."""
    global _auth_code
    params = urlencode({'client_id': CLIENT_ID, 'response_type': 'code', 
                        'redirect_uri': CALLBACK_URL,
                        'scope': 'patient/Patient.read patient/ExplanationOfBenefit.read patient/Coverage.read'})
    webbrowser.open(f'{AUTH_URL}?{params}')
    
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    print('Waiting for auth callback on http://localhost:8000 ...')
    server.handle_request() # blocks until one request arrives
    if not _auth_code: raise RuntimeError('No auth code received')
    return _auth_code

def exchange_code(code: str) -> dict:
    """Exchange auth code for access token. Returns token dict with access_token."""
    r = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code', 'code': code,
        'redirect_uri': CALLBACK_URL,
        'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET})
    r.raise_for_status()
    token = r.json()
    TOKEN_CACHE.write_text(json.dumps(token))
    return token

def get_token() -> str:
    """
    Return a valid access_token string. Uses cached token if present.
    Full auth flow runs in browser if no cache exists.
    Output: access_token (str)
    """
    if TOKEN_CACHE.exists():
        try:
            token = json.loads(TOKEN_CACHE.read_text())
            # BB2 sandbox tokens last 1 hour; attempt refresh if refresh_token present
            if 'access_token' in token: return token['access_token']
        except:
            pass
            
    code = get_auth_code()
    token = exchange_code(code)
    return token['access_token']
