from cryptography.fernet import Fernet
import json
from . import config


def split_to_chunks(data, key, chunk_size=4000):   
    if not isinstance(data, str):
        data = json.dumps(data)

    chunks = {}
    encrypted_chunks = {}
    
    for i in range(0, len(data), chunk_size):
        chunk_key = str(i // chunk_size)
        chunks[chunk_key] = data[i:i + chunk_size]
        
        encrypted_key = "PID"+str(chunk_key)
        encrypted_chunk = config.CIPHER_SUITE.encrypt(chunks[chunk_key].encode()).decode()
        
        encrypted_chunks[encrypted_key] = encrypted_chunk
    
    return encrypted_chunks

def combine_from_chunks(chunks, key):
    decrypted_chunks = {}
    
    for encrypted_key, encrypted_chunk in chunks.items():
        decrypted_key = int(encrypted_key.replace("PID", ""))
        decrypted_chunk = config.CIPHER_SUITE.decrypt(encrypted_chunk.encode()).decode()
        
        decrypted_chunks[decrypted_key] = decrypted_chunk

    sorted_keys = sorted(decrypted_chunks.keys())
    complete_data = ''.join(decrypted_chunks[key] for key in sorted_keys)

    return complete_data


def parse_to_dict(input_str):
    """
    Parses a semicolon-separated string into a dictionary.
    Each entry is separated by a semicolon, and each key-value pair is separated by an equal sign.

    Parameters:
        input_str (str): The input string to be parsed.

    Returns:
        dict: A dictionary containing the parsed key-value pairs.
    """
    # Split the input string by ";" to get individual entries
    entries = [input_str]
    if ";" in input_str:
        entries = input_str.split(";")
    # Initialize an empty dictionary to hold the key-value pairs
    parsed_dict = {}
    
    # Iterate over each entry and split it by "=" to get the key and value
    for entry in entries:
        if "=" in entry:
            key, value = entry.split("=", 1)  # Only split at the first "="
            parsed_dict[key] = value
    
    return parsed_dict

def dict_to_cookie_str(cookie_dict: dict) -> str:
    return "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])