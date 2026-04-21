# gap_report_generator.py
import pandas as pd
import sys
import os

# Add relevant directories to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fhir_field_mapper')))

from fhir_mapper import FHIRMapper

GAP_TAXONOMY = {
    None: ('No gap', 'Direct FHIR R4 mapping exists in US Core'),
    'no_equivalent': ('Structural gap', 'No FHIR R4 resource type exists for this concept'),
    'aggregation_gap': ('Aggregation gap', 'Resource exists but population-level aggregation not native to FHIR'),
    'custom_extension_required': ('Extension gap', 'Resource exists but granularity requires CMS-specific extension profile'),
    'partial_mapping': ('Partial mapping', 'Approximate mapping exists with known limitations'),
}

def build_gap_table(dataset: str = 'mssp_puf') -> pd.DataFrame:
    """
    Build a gap analysis DataFrame for all columns in a dataset.
    Input: dataset name string (must exist in FHIRMapper registry).
    Output: DataFrame with columns: column_name, fhir_resource, fhir_element_path, 
             cms_0057f_api, gap_category, gap_description, gap_notes.
    """
    mapper = FHIRMapper()
    rows = []
    for r in mapper.map_all(dataset):
        cat, desc = GAP_TAXONOMY.get(r.gap_type, ('Unknown', ''))
        rows.append({
            'MSSP PUF column': r.column_name,
            'FHIR resource': r.fhir_resource or '— none —',
            'FHIR element path': r.fhir_element_path or '— none —',
            'CMS-0057-F API': r.cms_0057f_api,
            'BB2 validated': r.us_core_validated,
            'Gap category': cat,
            'Gap notes': r.gap_notes,
        })
    return pd.DataFrame(rows)

def render_gap_report(df: pd.DataFrame, out_path: str = 'modules/puf_fhir_gap_analysis/output/gap_report.md'):
    """Write gap analysis table to Markdown file."""
    header = '# MSSP PUF to FHIR R4 Gap Analysis\n\n'
    
    summary = f'**{len(df)} fields analyzed**: '
    summary += f'**{(df["Gap category"]=="Structural gap").sum()} structural gaps**, '
    summary += f'**{(df["Gap category"]=="Extension gap").sum()} extension gaps**, '
    summary += f'**{(df["Gap category"]=="No gap").sum()} direct mappings**\n\n'
    
    md = header + summary + df.to_markdown(index=False)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, 'w') as f:
        f.write(md)
    print(f'Gap report written: {out_path}')
    return md

if __name__ == "__main__":
    df = build_gap_table()
    render_gap_report(df)
