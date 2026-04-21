# tests/test_fhir_mapper.py
import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fhir_mapper import FHIRMapper

@pytest.fixture
def mapper():
    return FHIRMapper()

def test_known_column(mapper):
    assert mapper.map('avg_risk_score').fhir_resource == 'RiskAssessment'

def test_structural_gap(mapper):
    assert mapper.map('sav_rate').gap_type == 'no_equivalent'

def test_no_gap(mapper):
    assert mapper.map('avg_risk_score').gap_type is None

def test_unknown_raises(mapper):
    with pytest.raises(KeyError):
        mapper.map('nonexistent_column')

def test_map_all_mssp(mapper):
    assert len(mapper.map_all('mssp_puf')) == 8

def test_get_gaps_filter(mapper):
    gaps = mapper.get_gaps('no_equivalent')
    assert any(g.column_name == 'sav_rate' for g in gaps)

def test_summary_has_no_equivalent(mapper):
    assert mapper.summary().get('no_equivalent', 0) >= 1
