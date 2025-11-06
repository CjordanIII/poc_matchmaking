
import json
def parse_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None
    
def to_json_string(data,location=""):
    try:
        with open(location, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2,sort_keys=True)
        return "Data successfully written to JSON file"
    except (TypeError, ValueError) as e:
        print(f"Error converting to JSON string: {e}")
        return None
    
    
