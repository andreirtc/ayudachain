import json,subprocess
from pathlib import Path
owned=json.loads((Path(__file__).resolve().parents[1]/'.runtime/usability-services.json').read_text())
for name in ['frontend','api']:
    subprocess.run(['taskkill','/PID',str(owned[name]),'/T','/F'],capture_output=True,timeout=20)
print('Stopped only the API/frontend trees started for this validation.')
