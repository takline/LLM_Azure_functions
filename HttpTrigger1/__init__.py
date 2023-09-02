import logging
import azure.functions as func
from cryptography.fernet import Fernet
import zlib
from typing import Union
import json
from datetime import datetime
import openai
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.functions._http import HttpRequestHeaders, HttpResponseHeaders

SERVICE_DISPATCHER = {
    "openai.ChatCompletion.create": lambda req: openai.ChatCompletion.create(**req),
    "openai.Audio.transcribe": lambda req: openai.Audio.transcribe(**req),
    # Add more services as needed
}
HEADERS_RESPONSE = {
    "statusCode": 201,
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    },
    "body": "https://www.google.com",
    "cookies": [],
}


OPENAI_FORMAT = {
    "id": "TODO",
    "parentid": "TODO",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "TODO",
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
}

def split_to_chunks(data, key, chunk_size=4000):
    cipher_suite = Fernet(key)
    
    if not isinstance(data, str):
        data = json.dumps(data)

    chunks = {}
    encrypted_chunks = {}
    
    for i in range(0, len(data), chunk_size):
        chunk_key = str(i // chunk_size)
        chunks[chunk_key] = data[i:i + chunk_size]
        
        encrypted_key = "PID"+str(chunk_key)
        encrypted_chunk = cipher_suite.encrypt(chunks[chunk_key].encode()).decode()
        
        encrypted_chunks[encrypted_key] = encrypted_chunk
    
    return encrypted_chunks

def combine_from_chunks(chunks, key):
    cipher_suite = Fernet(key)
    decrypted_chunks = {}
    
    for encrypted_key, encrypted_chunk in chunks.items():
        decrypted_key = int(encrypted_key.replace("PID", ""))
        decrypted_chunk = cipher_suite.decrypt(encrypted_chunk.encode()).decode()
        
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

def dict_to_cookie_str(cookie_dict: dict, domain: str = "azure.microsoft.com", expires: str = "Mon, 30-Sep-2024") -> str:
    """
    Convert a dictionary of cookies to a cookie string.
    
    Parameters:
        cookie_dict (dict): Dictionary of cookies.
        domain (str): The domain for the cookie.
        expires (str): The expiration date for the cookie.
    
    Returns:
        str: A string that can be used in the Set-Cookie header.
    """
    
    cookie_str = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
    
    if domain:
        cookie_str += f"; Domain={domain}"
    
    if expires:
        cookie_str += f"; Expires={expires}"
    
    return cookie_str+"13:55:09 GMT; Path=/; Max-Age=10000000"



def main(req: func.HttpRequest) -> func.HttpResponse:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://llms2155671127.vault.azure.net/", credential=credential)
    key = client.get_secret("ENCRYPTIONKEY").value

    cookie_header = req.headers.get('Cookie')
    if cookie_header is None:
        return func.HttpResponse(status_code=400)

    cookies1 = parse_to_dict(cookie_header)
    cookies2 = combine_from_chunks(cookies1, key)
    cookies3 = json.loads(cookies2)

    service_name = cookies3.get("service")
    if service_name not in SERVICE_DISPATCHER:
        return func.HttpResponse(f"Invalid service: {service_name}", status_code=400)

    # Prepare request for the specified service
    service_request = {
        "model": cookies3.get("model", "gpt-4"),
        "messages": cookies3.get("messages", [])
    }

    # Call the service and get the response
    service_response = SERVICE_DISPATCHER[service_name](service_request)

    # Structure the output based on the service
    if service_name == "openai.ChatCompletion.create":
        response_content = service_response["choices"][0]["message"]["content"]
    elif service_name == "openai.Audio.transcribe":
        response_content = service_response["transcription"]
    else:
        response_content = service_response

    # Use split_to_chunks to chunk the response
    chunked_response = split_to_chunks(response_content, key)

    # Prepare HttpResponse
    response = HEADERS_RESPONSE.copy()
    response["body"] = chunked_response

    return func.HttpResponse(json.dumps(response), status_code=201)
