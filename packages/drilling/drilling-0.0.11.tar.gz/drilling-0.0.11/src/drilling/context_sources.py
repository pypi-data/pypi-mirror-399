try: from drilling.context import *
except: from context import *
import yaml

def ConPrm(name, context=PARAMS.get('ClientContext', 'NotDefined'), arc_path = None):

    if not CONTEXT:  path = name
    else:
        connection = CONTEXT['CLIENT_CONTEXT']['Connections'][name] 
        path = CONTEXT['CONNECTIONS'] / f'{connection}.yaml'

    if arc_path: path = arc_path

    try:
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return data
    except: ValueError(f"Context Source {name} not found in {context}.yaml")

if __name__ == "__main__":
    print(ConPrm('Datalake'))