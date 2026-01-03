import sys
from pathlib import Path
import ipynbname
import yaml
import shutil
import os

try: 
    FILE_PATH = Path(ipynbname.path()).parent
    FILE_NAME = Path(ipynbname.path()).name
except: 
    FILE_PATH = Path(sys.argv[0]).parent
    FILE_NAME = Path(sys.argv[0]).name

ENABLE_CONTEXT = False
try: # Context Locator

    for c in range(10):
        root = FILE_PATH / "params.yaml" if c == 0 else FILE_PATH.parents[c-1] / "params.yaml"
        if root.is_file():
            sys.path.append(str(root.parent))
            with open(root, "r", encoding="utf-8") as f: 
                parameters = yaml.safe_load(f); break;
    
    PARAMS = parameters['Settings']
    ENABLE_CONTEXT = True

except: PARAMS = {}


try:
    if ENABLE_CONTEXT:
        try:
            with open(Path(PARAMS.get('ContextManager')) / 'clients' / f"{PARAMS.get('ClientContext')}.yaml" , "r", encoding="utf-8") as f: 
                CLIENT_CONTEXT = yaml.safe_load(f)
        except:  CLIENT_CONTEXT = {}

        CONTEXT = {
            'BASE_PATH': Path(PARAMS.get('ContextManager')),
            'CONNECTIONS': Path(PARAMS.get('ContextManager')) / 'connections',
            'ARCHIVES': Path(PARAMS.get('ContextManager')) / 'archives',
            'CLIENT_NAME': PARAMS.get('ClientContext', 'NotDefined'),
            'CLIENT_CONTEXT': CLIENT_CONTEXT
        }
        
except: CONTEXT = {}

        


if __name__ == "__main__":
    print(FILE_PATH)
    print(FILE_NAME)
    print(ENABLE_CONTEXT)
    print(PARAMS)
    print(CONTEXT)


