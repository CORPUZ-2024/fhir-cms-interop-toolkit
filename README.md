# interop-toolkit: FHIR Interoperability Portfolio

A collection of tools and libraries for health IT engineers and interoperability analysts focusing on CMS-0057-F compliance, FHIR R4 mapping, and gap analysis between CMS flat-file datasets and standard FHIR APIs.

## Project Overview

This toolkit provides automated workflows to validate payer transparency disclosures, map CMS public use files (PUF) to FHIR resources, and analyze structural gaps in current interoperability standards. It is designed to assist teams working on CMS-0057-F compliance and value-based care (VBC) data standardization.

## Modules

### 1. CMS-0057-F PA Metrics Compliance Checker
Validates publicly posted Prior Authorization (PA) metrics disclosures (PDF/HTML) against CMS-0057-F requirements.
- **Location**: `modules/pa_compliance_checker/`
- **Features**: Automated scraping of payer disclosures, extraction of 7 CMS-required metric fields, and validation of schema/math.
- **Output**: Generates a Markdown compliance report table in `output/compliance_report.md`.

### 2. FHIR R4 Field Mapping Library
A reusable library to map CMS flat-file column names to FHIR R4 resources and element paths.
- **Location**: `modules/fhir_field_mapper/`
- **Features**: Queryable registry of mappings, US Core IG v7 validation, and gap type categorization (e.g., structural, aggregation, or extension gaps).

### 3. CMS Blue Button 2.0 Sandbox Integration
Integration with the CMS Blue Button 2.0 API to validate FHIR mappings against live sandbox data.
- **Location**: `modules/bb2_sandbox/`
- **Features**: SMART on FHIR OAuth2 flow, automated queries for Patient, EOB, and Coverage resources, and comparison against expected mappings.
- **Setup**: Requires registration at [CMS Blue Button Developers](https://bluebutton.cms.gov/developers/).

### 4. CMS Flat-File to FHIR Gap Analysis
Synthesizes mapping and API results into a formal gap analysis and policy implications report.
- **Location**: `modules/puf_fhir_gap_analysis/`
- **Features**: Generates structured gap reports and prose analysis of policy implications for VBC data standardization.
- **Output**: `modules/puf_fhir_gap_analysis/output/gap_report.md` and `policy_implications.md`.

## Getting Started

### Prerequisites
- Python 3.9+
- Blue Button 2.0 Sandbox credentials (for Module 3)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/interop-toolkit.git
   cd interop-toolkit
   ```

2. Install dependencies:
   ```bash
   pip install requests pdfplumber beautifulsoup4 pandas openpyxl fhir.resources python-dotenv pytest notebook ipykernel
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:
   ```env
   BB2_CLIENT_ID=your_id_here
   BB2_CLIENT_SECRET=your_secret_here
   BB2_CALLBACK_URL=http://localhost:8000/callback
   ```

## Usage

### Run PA Compliance Checker
```bash
python modules/pa_compliance_checker/run_all.py
```

### Run Gap Analysis Report
```bash
python -c "from modules.puf_fhir_gap_analysis.gap_report_generator import build_gap_table, render_gap_report; render_gap_report(build_gap_table())"
```

## Testing
Run the full test suite using `pytest`:
```bash
pytest modules/ -v
```

## Acknowledgments
- Based on the CORPUZ-2024 FHIR Interoperability Portfolio Project Plan.
