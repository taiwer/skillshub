#!/usr/bin/env python3
"""批量 PubChem SMILES 查询脚本。读取 compounds.csv，通过 PUG-REST API 查询每个化合物的 SMILES，输出 compounds_with_smiles.csv。"""

import csv, urllib.request, urllib.parse, json, time, sys

INPUT = "01_Data/compounds.csv"
OUTPUT = "01_Data/compounds_with_smiles.csv"

def query_pubchem(name):
    """Query PubChem by name, return (smiles, iupac, cid, method)"""
    encoded = urllib.parse.quote(name, safe='')

    # Strategy 1: Direct name query
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/property/SMILES,IUPACName,MolecularFormula/JSON"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        props = data['PropertyTable']['Properties'][0]
        smiles = props.get('SMILES', '')
        iupac = props.get('IUPACName', '')
        cid = props.get('CID', '')
        return smiles, iupac, cid, 'pubchem_direct'
    except Exception:
        pass

    # Strategy 2: CID fallback
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/cids/JSON"
    try:
        req = urllib.request.Request(cid_url)
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        cids = data.get('IdentifierList', {}).get('CID', [])
        if cids:
            cid = cids[0]
            prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/SMILES,IUPACName,MolecularFormula/JSON"
            req2 = urllib.request.Request(prop_url)
            resp2 = urllib.request.urlopen(req2, timeout=30)
            data2 = json.loads(resp2.read())
            props = data2['PropertyTable']['Properties'][0]
            smiles = props.get('SMILES', '')
            iupac = props.get('IUPACName', '')
            return smiles, iupac, cid, 'pubchem_cid'
    except Exception:
        pass

    return '', '', '', 'not_found'

def main():
    compounds = []
    with open(INPUT, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            compounds.append(row)

    print(f"Querying {len(compounds)} compounds...")

    results = []
    for i, c in enumerate(compounds):
        name = c['Name']
        formula_from_data = c.get('Formula', '')
        smiles, iupac, cid, method = query_pubchem(name)

        # Check formula match
        pubchem_formula = ''
        formula_match = ''
        if cid and smiles:
            try:
                f_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula/JSON"
                resp = urllib.request.urlopen(urllib.request.Request(f_url), timeout=15)
                fdata = json.loads(resp.read())
                pubchem_formula = fdata['PropertyTable']['Properties'][0].get('MolecularFormula', '')
                if formula_from_data and pubchem_formula:
                    fm1 = formula_from_data.replace(' ', '')
                    fm2 = pubchem_formula.replace(' ', '')
                    formula_match = 'yes' if fm1 == fm2 else 'no'
            except Exception:
                pass

        row_out = {
            'No': c['No'], 'Name': name, 'Formula': formula_from_data,
            'SMILES': smiles, 'IUPAC': iupac, 'CID': str(cid) if cid else '',
            'Method': method, 'FormulaMatch': formula_match, 'Source': c.get('Source', '')
        }
        results.append(row_out)

        status = '✓' if smiles else '✗'
        print(f"  {i+1:2d}/{len(compounds)} {status} {name[:45]:<45s}")
        if i < len(compounds) - 1:
            time.sleep(0.4)

    fieldnames = ['No', 'Name', 'Formula', 'SMILES', 'IUPAC', 'CID', 'Method', 'FormulaMatch', 'Source']
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(results)

    found = sum(1 for r in results if r['SMILES'])
    print(f"\nDone: {found}/{len(compounds)} compounds have SMILES")
    print(f"Output: {OUTPUT}")

if __name__ == '__main__':
    main()
