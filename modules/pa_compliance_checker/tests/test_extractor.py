# tests/test_extractor.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pa_field_extractor import extract_rate, extract_text_from_html, PAMetricsRaw, RATE_PATTERNS
from pathlib import Path
import tempfile

def test_extract_rate_standard_approved():
    text = "Standard requests approved: 92.3%"
    assert extract_rate(text, 'standard_approved_pct') == 92.3

def test_extract_rate_standard_denied():
    text = "Standard requests denied 7.7%"
    assert extract_rate(text, 'standard_denied_pct') == 7.7

def test_extract_rate_expedited_approved():
    text = "Expedited approved: 89.1%"
    assert extract_rate(text, 'expedited_approved_pct') == 89.1

def test_extract_rate_appeal_overturn():
    text = "Overturned on appeal: 61.2%"
    assert extract_rate(text, 'approved_after_appeal_pct') == 61.2

def test_extract_rate_returns_none_when_not_found():
    assert extract_rate("No percentages here", 'standard_approved_pct') is None

def test_extract_from_html():
    html = "<html><body>Standard requests approved: 88.5% Standard requests denied 11.5%</body></html>"
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False, encoding='utf-8') as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        result = extract_text_from_html(tmp)
        assert '88.5' in result
    finally:
        tmp.unlink()

def test_extract_full_returns_dataclass():
    # Each metric on its own line to prevent greedy regex cross-contamination.
    # standard.*approv with re.DOTALL would otherwise consume into
    # "Expedited approved" and return its percentage instead.
    html = (
        "<html><body>"
        "Standard prior authorization requests approved: 88.5%\n"
        "Standard prior authorization requests denied: 11.5%\n"
        "</body></html>"
    )
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False, encoding='utf-8') as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        from pa_field_extractor import extract
        result = extract(tmp, 'test_payer')
        assert isinstance(result, PAMetricsRaw)
        assert result.payer_key == 'test_payer'
        assert result.standard_approved_pct == 88.5
        assert result.standard_denied_pct == 11.5
    finally:
        tmp.unlink()

# Run: pytest modules/pa_compliance_checker/tests/ -v
