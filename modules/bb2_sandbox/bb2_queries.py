# bb2_queries.py — FHIR resource query functions
import requests, json
from pathlib import Path

FHIR_BASE = 'https://sandbox.bluebutton.cms.gov/v2/fhir'
CACHE_DIR = Path('modules/bb2_sandbox/data/bb2_responses')

def _get(path: str, token: str, params: dict = None) -> dict:
    """Single authenticated FHIR GET. Raises on non-200."""
    r = requests.get(f'{FHIR_BASE}{path}', params=params,
                     headers={'Authorization': f'Bearer {token}', 
                              'Accept': 'application/fhir+json'})
    if r.status_code == 403: raise PermissionError('Token expired or wrong scope -- re-auth')
    if r.status_code == 400: raise ValueError(f'Bad request: {r.text[:200]}')
    r.raise_for_status()
    return r.json()

def get_patient(token: str) -> dict:
    """
    Query the Patient resource for the authenticated synthetic beneficiary.
    Output: FHIR Patient resource dict.
    Key fields: id (bene_id), name, birthDate, gender.
    """
    result = _get('/Patient', token)
    _cache(result, 'patient')
    return result

def get_eob(token: str, count: int = 50) -> list[dict]:
    """
    Query all ExplanationOfBenefit resources for the authenticated beneficiary.
    Handles Bundle pagination via Bundle.link[relation='next'].
    Input: count — page size (default 50, max 50 per BB2 docs).
    Output: list of EOB resource dicts (unpacked from Bundle).
    """
    results = []
    data = _get('/ExplanationOfBenefit', token, {'_count': count})
    while True:
        results.extend(e['resource'] for e in data.get('entry', []))
        next_url = next((l['url'] for l in data.get('link',[]) if l['relation']=='next'), None)
        if not next_url: break
        r = requests.get(next_url, headers={'Authorization': f'Bearer {token}', 
                                           'Accept': 'application/fhir+json'})
        r.raise_for_status()
        data = r.json()
    
    _cache({'resourceType': 'Bundle', 'entry': [{'resource': r} for r in results]}, 'eob')
    print(f'Retrieved {len(results)} EOB resources')
    return results

def get_coverage(token: str) -> list[dict]:
    """
    Query Coverage resources for the authenticated beneficiary.
    Output: list of Coverage resource dicts.
    """
    data = _get('/Coverage', token)
    _cache(data, 'coverage')
    return [e['resource'] for e in data.get('entry', [])]

def _cache(data: dict, name: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f'{name}.json'
    path.write_text(json.dumps(data, indent=2))
