# run_all.py — end-to-end pipeline entry point
from pa_disclosure_scraper import fetch_all
from pa_field_extractor import extract
from pa_compliance_validator import validate
from pa_report_generator import save_report

def main():
    files = fetch_all() # Step 1: fetch/load disclosures
    all_results = []
    
    for payer_key, path in files.items():
        raw = extract(path, payer_key) # Step 2: extract 7 fields
        results = validate(raw) # Step 3: validate
        all_results.extend(results)
        print(f'{payer_key}: {sum(r.status=="FAIL" for r in results)} FAIL, '
              f'{sum(r.status=="MISSING" for r in results)} MISSING')
              
    save_report(all_results) # Step 4: output Markdown table

if __name__ == '__main__':
    main()
