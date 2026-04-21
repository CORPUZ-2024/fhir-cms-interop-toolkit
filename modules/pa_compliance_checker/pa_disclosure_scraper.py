# pa_disclosure_scraper.py
import requests, os, time
from pathlib import Path

PAYERS = {
    'molina_ca': 'https://www.molinahealthcare.com/providers/ca/medicaid/prior-auth/metrics',
    'lacare': 'https://www.lacare.org/providers/prior-authorization/metrics',
    'caloptima': 'https://www.caloptima.org/prior-auth-metrics',
    'bsca': 'https://www.blueshieldca.com/providers/prior-auth-metrics',
}

SAVE_DIR = Path('modules/pa_compliance_checker/data/payer_disclosures')

def fetch_disclosure(payer_key: str, url: str) -> Path:
    """
    Fetch a payer disclosure page and save to disk.
    Returns: Path to saved file.
    Raises: requests.HTTPError on non-200 response.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (research/compliance-checker)'}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    
    ext = '.pdf' if 'pdf' in r.headers.get('Content-Type','') else '.html'
    out = SAVE_DIR / f'{payer_key}_2025{ext}'
    out.write_bytes(r.content)
    print(f'Saved {payer_key}: {len(r.content):,} bytes -> {out}')
    return out

def fetch_all(delay_sec: float = 1.5) -> dict[str, Path]:
    """Fetch all payers. Returns {payer_key: Path}. Skips if file exists."""
    results = {}
    for key, url in PAYERS.items():
        existing = list(SAVE_DIR.glob(f'{key}_2025.*'))
        if existing:
            print(f'Skip {key}: already saved at {existing[0]}')
            results[key] = existing[0]
            continue
        try:
            results[key] = fetch_disclosure(key, url)
        except Exception as e:
            print(f'Error fetching {key}: {e}')
            # Manual fallback mentioned in plan: check if file was manually placed
            if existing:
                results[key] = existing[0]
        time.sleep(delay_sec)
    return results

if __name__ == '__main__':
    fetch_all()
