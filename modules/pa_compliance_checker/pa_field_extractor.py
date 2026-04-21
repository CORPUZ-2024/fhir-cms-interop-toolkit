# pa_field_extractor.py
import pdfplumber, re
from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# The 7 required CMS-0057-F fields (source: CMS PA API FAQ)
FIELD_KEYS = [
    'pa_required_list',            # F1: list of PA-required items (not a rate)
    'standard_approved_pct',       # F2: % standard requests approved
    'standard_denied_pct',         # F3: % standard requests denied
    'approved_after_appeal_pct',   # F4: % approved after appeal (denom = denied)
    'extended_review_approved_pct',# F5: % extended review then approved
    'expedited_approved_pct',      # F6: % expedited approved
    'expedited_denied_pct',        # F7: % expedited denied
]

@dataclass
class PAMetricsRaw:
    payer_key: str
    source_path: str
    pa_required_list: Optional[str] = None # raw text list
    standard_approved_pct: Optional[float] = None
    standard_denied_pct: Optional[float] = None
    approved_after_appeal_pct: Optional[float] = None
    extended_review_approved_pct: Optional[float] = None
    expedited_approved_pct: Optional[float] = None
    expedited_denied_pct: Optional[float] = None
    extraction_notes: list = field(default_factory=list)

RATE_PATTERNS = {
    'standard_approved_pct': [r'standard.*approv.*?(\d+\.?\d*)\s*%'],
    'standard_denied_pct': [r'standard.*deni.*?(\d+\.?\d*)\s*%'],
    'approved_after_appeal_pct': [r'appeal.*approv.*?(\d+\.?\d*)\s*%', 
                                  r'overtur.*?(\d+\.?\d*)\s*%'],
    'extended_review_approved_pct': [r'extend.*review.*?(\d+\.?\d*)\s*%'],
    'expedited_approved_pct': [r'expedit.*approv.*?(\d+\.?\d*)\s*%'],
    'expedited_denied_pct': [r'expedit.*deni.*?(\d+\.?\d*)\s*%'],
}

def extract_text_from_pdf(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        return '\n'.join(page.extract_text() or '' for page in pdf.pages)

def extract_text_from_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def extract_rate(text: str, field_key: str) -> Optional[float]:
    """Try each regex pattern for a field. Return first match as float, or None."""
    for pattern in RATE_PATTERNS[field_key]:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            return float(m.group(1))
    return None

def extract(path: Path, payer_key: str) -> PAMetricsRaw:
    """
    Extract all 7 PA metric fields from a PDF or HTML disclosure file.
    Input: Path to saved disclosure file, payer identifier string.
    Output: PAMetricsRaw dataclass. None values = field not found.
    """
    text = extract_text_from_pdf(path) if path.suffix == '.pdf' else extract_text_from_html(path)
    result = PAMetricsRaw(payer_key=payer_key, source_path=str(path))
    
    for field_key in RATE_PATTERNS:
        val = extract_rate(text, field_key)
        setattr(result, field_key, val)
        if val is None:
            result.extraction_notes.append(f'{field_key}: not found via regex')
            
    # F1 is a list, not a rate — search for a structured list near 'prior authorization'
    f1_m = re.search(r'items?.{0,80}(services?: procedures?).{0,500}', text, re.IGNORECASE | re.DOTALL)
    result.pa_required_list = f1_m.group(0)[:400].strip() if f1_m else None
    
    return result
