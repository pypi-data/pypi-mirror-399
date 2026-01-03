import yaml, json, traceback, os

def load_config(path: str):
    try:
        with open(path, "r", encoding="utf-8") as file:
            context = file.read()
            if path[-4:] == "json":
                context = context.replace("\n","").replace("    ","")
                loaded_data = json.loads(context)
            elif path[-4:] == "yaml":
                loaded_data = yaml.safe_load(context)
            else:
                print("Error file type")
        if not loaded_data: raise FileNotFoundError()
        return loaded_data
    except FileNotFoundError: 
        dump_config(path, {})
        return load_config(path)
    except: traceback.print_exc()

def dump_config(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as file:
            if path[-4:] == "json":
                file.write(_dict_to_json(data))
            elif path[-4:] == "yaml":
                yaml.safe_dump(data, file)
            else: print("Error file type")
    except FileNotFoundError:
        dictionary = path.split("/")
        now_path = ""
        for dicts in dictionary[:-1]:
            try: os.mkdir(f"{now_path}{dicts}/")
            except: pass
            now_path+=dicts+"/"
        dump_config(path = path, data = data)
    except: traceback.print_exc()

def _dict_to_json(data,level=0):
    json_str = ""
    tap = "    "
    if type(data) == dict:
        json_str += "{"
        for idx in range(len(data)):
            json_str += "\n"
            key = list(data.keys())[idx]
            json_str += (tap * (level+1))
            json_str += f'"{key}":{_dict_to_json(data[key],(level+1))}'
            if idx < len(data)-1:
                json_str += f","
        if len(data) > 0:
            json_str += "\n"
            json_str += "    " * (level)
        json_str += "}"
    elif type(data) == list:
        json_str = "["
        for idx in range(len(data)):
            json_str += "\n"
            json_str += (tap * (level+1))
            json_str += _dict_to_json(data[idx], (level+1))
            if idx < len(data)-1:
                json_str += f","
        if len(data) > 0:
            json_str += "\n"
            json_str += "    " * (level)
        json_str += "]"
    elif type(data) == str:
        json_str = f'"{data}"'
    else:
        json_str = f"{data}"
    if not json_str.strip():
        json_str = "{}"
    return json_str