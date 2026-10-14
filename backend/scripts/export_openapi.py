import json
from backend.app.main import app
from backend.app.config import ROOT

if __name__=='__main__':
    path=ROOT/'shared/protocol/openapi.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(app.openapi(),indent=2)+'\n',encoding='utf-8')
