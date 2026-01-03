import os
import pyotp
import requests
from dotenv import load_dotenv

def get_session_token():
    load_dotenv()
    api_key = os.getenv("TRADEJINI_API_KEY")
    password = os.getenv("TRADEJINI_PASSWORD")
    totp_secret = os.getenv("TRADEJINI_TOTP_SECRET")
    
    if not all([api_key, password, totp_secret]):
        raise Exception("Missing credentials in .env. Run 'tradejini-setup' first.")

    totp = pyotp.TOTP(totp_secret).now()
    url = "https://api.tradejini.com/v2/api-gw/oauth/individual-token-v2"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {'password': password, 'twoFa': totp, 'twoFaTyp': 'totp'}
    
    res = requests.post(url, data=payload, headers=headers)
    if res.status_code == 200:
        return f"{api_key}:{res.json().get('access_token')}"
    raise Exception(f"Authentication Failed: {res.text}")