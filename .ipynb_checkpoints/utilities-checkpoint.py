from json import loads, JSONDecodeError, dump
from ast import literal_eval
from re import sub, match

def reformat_json(input_json: str) -> str:
    try:
        parsed_data = loads(input_json)
        nested_json_str = parsed_data.get("json", "")

        nested_json_str = sub(r'(\d),(\d)', r'\1.\2', nested_json_str)

        return nested_json_str
    
    except JSONDecodeError as e:
        return f"Error parsing JSON: {e}"

def parse_input(input_str):
    # First, let's clean the input string of any leading/trailing whitespaces
    input_str = input_str.strip()
    
    try:
        # Use ast.literal_eval() to safely evaluate the string into a Python object (list or dict)
        parsed_object = literal_eval(input_str)
        
        # Now, we can check if it's a list and if each item is a dictionary that needs more parsing
        if isinstance(parsed_object, list):
            for i in range(len(parsed_object)):
                if isinstance(parsed_object[i], dict):
                    # Here you can process individual dictionary entries if needed
                    # For example, converting values like '1.00' into actual numbers or percentages
                    for key, value in parsed_object[i].items():
                        # Convert numeric strings to floats if possible
                        if isinstance(value, str):
                            value = value.strip()
                            if match(r"^\d+(\.\d+)?$", value):  # Check if it's a valid number
                                parsed_object[i][key] = float(value)
                            elif match(r"^\d+(\.\d+)?%$", value):  # Check if it's a percentage
                                parsed_object[i][key] = value
                            # If needed, other conversions (e.g., dates or specific formats) can be added here
        return parsed_object
    
    except Exception as e:
        raise ValueError(f"Error parsing input: {e}")

def save_json_to_file(data, filename):
    # Save the JSON data to a file
    try:
        with open(filename, 'w') as f:
            dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving file: {e}")

def process_and_save_records(train_data):
    merged_data = {}  # Initialize an empty list to hold all parsed records

    for idx, row in train_data.iterrows():
        print(idx)
        try:

            formatted_json = reformat_json(row.iloc[2])
            formatted_json = parse_input(formatted_json)
            
            if isinstance(formatted_json, dict):
                save_json_to_file(formatted_json, f'train_invoices-and-receipts_ocr_v1/parsed_data(reformulated)/record_{idx}.json')
            
            else:
                raise TypeError("Unexpected Error Occured! ")
                
        except Exception as e:
            print(f"Error processing record: {e}")

def compare_items(item_1, item_2):

    if isinstance(item_1, dict) and isinstance(item_2, dict):
        if set(item_1.keys()) != set(item_2.keys()):
            return False
        for key in item_1:
            val_1 = item_1[key]
            val_2 = item_2[key]
            if not compare_items(val_1, val_2):
                return False
    
    elif isinstance(item_1, list) and isinstance(item_2, list):
        for val_1, val_2 in zip(item_1, item_2):
            if not compare_items(val_1, val_2):
                return False
    
    elif type(item_1) != type(item_2):
        return False
    
    return True

get_dict_from = (lambda row: parse_input(reformat_json(row)))

def generate_signature(item):
    """
    Generate a unique signature for the structure of the given item (dictionary, list, or primitive).
    """
    if isinstance(item, dict):
        # Create a signature based on the dictionary's keys and the type of their values
        signature = {}
        for key, value in item.items():
            signature[key] = generate_signature(value)  # Recursively generate signature for the value
        return tuple(sorted(signature.items()))  # Sort to ensure order doesn't affect uniqueness

    elif isinstance(item, list):
        # Create a signature based on the types of elements in the list
        if not item:  # If list is empty, treat it as an empty type
            return ('list',)
        # Extract the type signature of the first element (if all items have the same structure)
        element_signature = generate_signature(item[0])
        return ('list', element_signature)  # Signature for list, using the element type signature

    else:
        # Return a tuple with the type of the item for primitive types (int, str, etc.)
        return (type(item).__name__,)

