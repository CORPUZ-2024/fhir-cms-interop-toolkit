# fhir_mapper.py
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

MAPPINGS_DIR = Path('modules/fhir_field_mapper/data/mappings')

@dataclass
class MappingResult:
    column_name: str
    dataset: str
    fhir_resource: Optional[str]
    fhir_element_path: Optional[str]
    cms_0057f_api: str
    us_core_validated: str # 'yes', 'partial', 'no', 'gap'
    gap_type: Optional[str] # null, 'no_equivalent', 'partial_mapping', 'custom_extension_required', 'aggregation_gap'
    gap_notes: str

class FHIRMapper:
    """
    Maps CMS flat-file column names to FHIR R4 equivalents.
    Usage:
    mapper = FHIRMapper()
    result = mapper.map('avg_risk_score') # single lookup
    df = mapper.map_all('mssp_puf') # all columns for a dataset
    gaps = mapper.get_gaps(gap_type='no_equivalent') # filter by gap type
    """
    def __init__(self, mappings_dir: Optional[Path] = None):
        self._registry: dict[str, dict] = {} # {column_name: record}
        self.mappings_dir = mappings_dir or MAPPINGS_DIR
        self._load_all()

    def _load_all(self):
        """Load all JSON mapping files from data/mappings/."""
        for f in self.mappings_dir.glob('*.json'):
            if f.stem == 'schema': continue
            try:
                records = json.loads(f.read_text())
                for rec in records:
                    self._registry[rec['column_name']] = rec
            except Exception as e:
                print(f"Error loading {f}: {e}")
        print(f'FHIRMapper: loaded {len(self._registry)} column mappings')

    def map(self, column_name: str) -> MappingResult:
        """
        Look up a single column name.
        Input: column_name (str) — exact match to column_name field in JSON.
        Output: MappingResult dataclass.
        Raises: KeyError if column not in registry.
        """
        if column_name not in self._registry:
            raise KeyError(f"Column '{column_name}' not in registry. "
                           f"Available: {list(self._registry.keys())}")
        r = self._registry[column_name]
        return MappingResult(**{k: r.get(k) for k in MappingResult.__dataclass_fields__})

    def map_all(self, dataset: str = None) -> list[MappingResult]:
        """Return all mappings, optionally filtered by dataset name."""
        records = self._registry.values()
        if dataset:
            records = [r for r in records if r['dataset'] == dataset]
        return [MappingResult(**{k: r.get(k) for k in MappingResult.__dataclass_fields__}) 
                for r in records]

    def get_gaps(self, gap_type: str = None) -> list[MappingResult]:
        """Return all fields with a gap_type, optionally filtered by type."""
        return [r for r in self.map_all() 
                if r.gap_type and (gap_type is None or r.gap_type == gap_type)]

    def summary(self) -> dict:
        """Return counts by gap_type for quick overview."""
        from collections import Counter
        return dict(Counter(r.gap_type or 'no_gap' for r in self.map_all()))
