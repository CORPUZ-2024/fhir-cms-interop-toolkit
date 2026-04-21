# us_core_validator.py
# Checks whether a FHIR element path exists in the US Core IG v7 StructureDefinition
import requests, json

US_CORE_BASE = 'https://hl7.org/fhir/us/core/STU7/StructureDefinition-'

def check_element_path(resource: str, element_path: str) -> dict:
    """
    Query US Core IG StructureDefinition for a resource and check if 
    the given element path exists.
    Input: resource (str) e.g. 'ExplanationOfBenefit'
           element_path (str) e.g. '.total.amount.value'
    Output: dict with keys: resource, element_path, found (bool), note (str)
    """
    url = f'{US_CORE_BASE}us-core-{resource.lower()}.json'
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 404:
            return {'resource': resource, 'element_path': element_path, 
                    'found': False, 'note': f'No US Core profile for {resource}'}
        
        sd = r.json()
        # Element paths in StructureDefinition are in snapshot.element[].path
        elements = [e['path'] for e in sd.get('snapshot', {}).get('element', [])]
        clean_path = resource + element_path # e.g. 'ExplanationOfBenefit.total.amount.value'
        found = any(e == clean_path or e.startswith(clean_path) for e in elements)
        
        return {'resource': resource, 'element_path': element_path, 
                'found': found, 'note': '' if found else 'Path not in US Core snapshot'}
    except Exception as ex:
        return {'resource': resource, 'element_path': element_path, 
                'found': False, 'note': str(ex)}
