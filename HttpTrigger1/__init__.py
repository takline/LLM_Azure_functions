import logging

import azure.functions as func
from cryptography.fernet import Fernet
import zlib
from typing import Union
import json
from datetime import datetime
import openai
from OpenAIAuth import Auth0


def login_to_openai():
    auth = Auth0(email_address=client.get_secret("OPENAIUSERNAME").value, password=client.get_secret("OPENAIPW").value)
    access_token = auth.get_access_token()
    return access_token

def encode_to_utf8(current_log, data):
    if isinstance(data, (dict, list)):
        return current_log+"\n"+json.dumps(data).encode('utf-8')
    elif isinstance(data, str):
        return current_log+"\n"+data.encode('utf-8')
    elif isinstance(data, (int, float)):
        return current_log+"\n"+str(data).encode('utf-8')
    else:
        raise ValueError("Unsupported data type. Please provide a dictionary, list, or string.")

HEADERS_RESPONSE = {
    "statusCode": 201,
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    },
    "body": "https://www.google.com",
    "cookies": [],
}

input_mapping_order = {
    "service": 0,
    "model": 1,
    "messages": 2,
    "prompt": 3,
    "conversation_id": 4,
    "previous_convo_id": 5,
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


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    cipher_suite = Fernet(client.get_secret("ENCRYPTIONKEY").value)

    encrypted_input = req.cookies.get("payload")
    #req_body = req.get_json()
    decrypted_input_str = cipher_suite.decrypt(encrypted_input.encode()).decode()

    return func.HttpResponse(body="", cookies={"result": encrypted_output})

