"""Bounded subprocess text extraction. Images/scans always need manual review."""
import json
import re
import sys
from decimal import Decimal
from pypdf import PdfReader


def extract(path):
    reader=PdfReader(path,strict=True)
    if reader.is_encrypted or len(reader.pages)>100: raise ValueError('Manual review required')
    parts=[]
    for page in reader.pages:
        parts.append(page.extract_text() or '')
        if sum(len(p) for p in parts)>65536: raise ValueError('Manual review required')
    text='\n'.join(parts)
    fields={'text':text}
    patterns={'reference_number':r'(?:Reference|Ref)\s*[:#]\s*([^\n]+)',
              'issued_date':r'(?:Issued|Date)\s*:\s*(\d{4}-\d{2}-\d{2})',
              'purpose':r'Purpose\s*:\s*([^\n]+)','covered_area':r'(?:Area|Coverage)\s*:\s*([^\n]+)',
              'document_words':r'(?:In words|Amount in words)\s*:\s*([^\n]+)'}
    for key,pattern in patterns.items():
        m=re.search(pattern,text,re.I)
        if m: fields[key]=m[1].strip()
    amount=re.search(r'(?:Amount|Total)\s*:\s*(?:PHP|₱|P)?\s*([\d,]+(?:\.\d{1,2})?)',text,re.I)
    if amount: fields['amount_centavos']=str(int(Decimal(amount[1].replace(',',''))*100))
    return fields


if __name__=='__main__':
    try: print(json.dumps(extract(sys.argv[1]),ensure_ascii=False))
    except Exception: sys.exit(1)
