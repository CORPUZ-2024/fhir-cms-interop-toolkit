# pa_compliance_validator.py
from dataclasses import dataclass
from pa_field_extractor import PAMetricsRaw
from typing import Optional

@dataclass
class ValidationResult:
    payer_key: str
    field: str
    reported_value: Optional[float]
    expected: str
    status: str # 'PASS', 'FAIL', 'WARN', 'MISSING'
    note: str = ''

def validate(raw: PAMetricsRaw) -> list[ValidationResult]:
    """
    Apply all CMS-0057-F validation rules to a PAMetricsRaw record.
    Returns: list of ValidationResult, one per check.
    """
    results = []
    pk = raw.payer_key
    
    def check(field, value, expected_str, pass_fn, note=''):
        if value is None:
            results.append(ValidationResult(pk, field, None, expected_str, 'MISSING', 'Field not found in disclosure'))
            return
        status = 'PASS' if pass_fn(value) else 'FAIL'
        results.append(ValidationResult(pk, field, value, expected_str, status, note))

    # Rule 1: All rate fields must be 0–100
    rate_fields = ['standard_approved_pct','standard_denied_pct','approved_after_appeal_pct',
                   'extended_review_approved_pct','expedited_approved_pct','expedited_denied_pct']
    for f in rate_fields:
        v = getattr(raw, f)
        check(f, v, '0–100 numeric', lambda x: 0 <= x <= 100)
        
    # Rule 2: F2 + F3 must sum to 100 (±0.5 tolerance for rounding)
    if raw.standard_approved_pct is not None and raw.standard_denied_pct is not None:
        s = raw.standard_approved_pct + raw.standard_denied_pct
        results.append(ValidationResult(pk, 'F2+F3 sum', s, '100 ±0.5', 
                                     'PASS' if abs(s - 100) <= 0.5 else 'FAIL',
                                     f'F2={raw.standard_approved_pct} + F3={raw.standard_denied_pct} = {s:.1f}'))
        
    # Rule 3: F6 + F7 must sum to 100 (±0.5 tolerance)
    if raw.expedited_approved_pct is not None and raw.expedited_denied_pct is not None:
        s = raw.expedited_approved_pct + raw.expedited_denied_pct
        results.append(ValidationResult(pk, 'F6+F7 sum', s, '100 ±0.5', 
                                     'PASS' if abs(s - 100) <= 0.5 else 'FAIL',
                                     f'F6={raw.expedited_approved_pct} + F7={raw.expedited_denied_pct} = {s:.1f}'))
        
    # Rule 4: F4 denominator flag — we cannot verify denominator from the disclosure
    # alone, but we can flag if F4 > 90% (implausibly high overturn rate, 
    # likely computed against total requests not total denials)
    if raw.approved_after_appeal_pct is not None:
        results.append(ValidationResult(pk, 'F4 denominator flag', raw.approved_after_appeal_pct,
                                     '<90% (implausibility threshold)',
                                     'WARN' if raw.approved_after_appeal_pct > 90 else 'PASS',
                                     'Value >90% suggests denominator may be total PA requests, not total denials (~12x error)'))
                                     
    # Rule 5: F1 must be present
    results.append(ValidationResult(pk, 'F1 pa_required_list', None, 
                                 'Non-empty text list', 'PASS' if raw.pa_required_list else 'MISSING'))
    
    return results
