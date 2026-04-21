# fhir_response_parser.py
# Extracts field values from raw FHIR responses into a flat dict 
# matching the FHIRMapper MappingResult schema for comparison.

def parse_patient(patient: dict) -> dict:
    """Extract key Patient fields as flat dict."""
    return {
        'bene_id': patient.get('id'),
        'birth_date': patient.get('birthDate'),
        'gender': patient.get('gender'),
    }

def parse_eob_total(eob_list: list[dict]) -> dict:
    """
    Aggregate EOB.total.amount.value across all EOBs.
    This approximates total_per_capita_exp from the MSSP PUF.
    Output: {'total_amount': float, 'eob_count': int, 'currency': str}
    """
    total = 0.0
    currency = None
    for eob in eob_list:
        for item in eob.get('total', []):
            amt = item.get('amount', {})
            total += float(amt.get('value', 0))
            currency = currency or amt.get('currency')
    return {'total_amount': round(total, 2), 'eob_count': len(eob_list), 'currency': currency}

def parse_coverage(coverage_list: list[dict]) -> dict:
    """
    Extract Coverage.type.coding.code — maps to enrollment_type in MSSP PUF.
    Expected gap: US Core Coverage.type uses a different value set than MSSP enrollment types.
    Output: {'coverage_type_codes': list, 'gap_confirmed': bool}
    """
    codes = []
    for cov in coverage_list:
        for coding in cov.get('type', {}).get('coding', []):
            codes.append(coding.get('code',''))
            
    mssp_types = {'ESRD', 'Disabled', 'Aged Dual', 'Aged Non-Dual'}
    found_codes = set(codes)
    gap_confirmed = not bool(found_codes & mssp_types) # True if no MSSP code found
    
    return {'coverage_type_codes': codes, 'gap_confirmed': gap_confirmed, 
            'gap_note': 'US Core Coverage.type codes do not include MSSP enrollment types' if gap_confirmed else ''}
