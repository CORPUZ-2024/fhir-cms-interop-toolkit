# tests/test_validator.py
import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pa_field_extractor import PAMetricsRaw
from pa_compliance_validator import validate

def make_raw(f2=92.3, f3=7.7, f4=61.2, f5=3.1, f6=89.1, f7=10.9):
    return PAMetricsRaw(
        payer_key='test', source_path='test.pdf',
        pa_required_list='DME, home health, inpatient, SNF',
        standard_approved_pct=f2, standard_denied_pct=f3,
        approved_after_appeal_pct=f4, extended_review_approved_pct=f5,
        expedited_approved_pct=f6, expedited_denied_pct=f7)

def test_f2_f3_sum_pass():
    results = validate(make_raw())
    assert all(r.status=='PASS' for r in results if r.field=='F2+F3 sum')

def test_f2_f3_sum_fail():
    results = validate(make_raw(f2=90, f3=5))
    assert any(r.status=='FAIL' for r in results if r.field=='F2+F3 sum')

def test_f4_denominator_warn():
    results = validate(make_raw(f4=95))
    assert any(r.status=='WARN' for r in results if 'denominator' in r.field)

def test_missing_field():
    results = validate(make_raw(f2=None))
    assert any(r.status=='MISSING' for r in results if 'standard_approved' in r.field)
