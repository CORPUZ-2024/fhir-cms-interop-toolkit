# tests/test_gap_taxonomy.py
import sys
import os

# Add relevant directories to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modules', 'fhir_field_mapper')))

from gap_report_generator import build_gap_table, render_gap_report

def test_gap_table_has_8_rows():
    df = build_gap_table('mssp_puf')
    assert len(df) == 8, f'Expected 8 rows, got {len(df)}'

def test_structural_gaps_identified():
    df = build_gap_table('mssp_puf')
    structural = df[df['Gap category'] == 'Structural gap']
    assert 'sav_rate' in structural['MSSP PUF column'].values

def test_no_gap_for_direct_mapping():
    df = build_gap_table('mssp_puf')
    no_gap = df[df['Gap category'] == 'No gap']
    assert 'avg_risk_score' in no_gap['MSSP PUF column'].values

def test_report_renders():
    df = build_gap_table('mssp_puf')
    out_path = 'modules/puf_fhir_gap_analysis/output/test_gap_report.md'
    md = render_gap_report(df, out_path)
    assert '# MSSP PUF to FHIR R4 Gap Analysis' in md
    assert 'sav_rate' in md
    if os.path.exists(out_path):
        os.remove(out_path)
