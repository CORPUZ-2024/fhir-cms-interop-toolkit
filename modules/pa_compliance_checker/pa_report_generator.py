# pa_report_generator.py
import pandas as pd
from pa_compliance_validator import ValidationResult

STATUS_EMOJI = {'PASS': 'OK', 'FAIL': 'FAIL', 'WARN': 'WARN', 'MISSING': 'MISS'}

def to_markdown_table(results: list[ValidationResult]) -> str:
    """Render validation results as a GitHub-renderable Markdown table."""
    rows = [{'Payer': r.payer_key, 'Field': r.field, 'Value': r.reported_value,
             'Expected': r.expected, 'Status': STATUS_EMOJI[r.status], 'Note': r.note}
            for r in results]
    return pd.DataFrame(rows).to_markdown(index=False)

def save_report(results: list[ValidationResult], out_path: str = 'output/compliance_report.md'):
    md = '# CMS-0057-F PA Metrics Compliance Report\n\n' + to_markdown_table(results)
    with open(out_path, 'w') as f:
        f.write(md)
    print(f'Report saved: {out_path}')
