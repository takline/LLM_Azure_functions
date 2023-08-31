import logging
import azure.functions as func
from cryptography.fernet import Fernet
import zlib
from typing import Union
import json
from datetime import datetime
import openai
from OpenAIAuth import Auth0
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from http.cookies import SimpleCookie

def login_to_openai():
    auth = Auth0(email_address=client.get_secret("OPENAIUSERNAME").value, password=client.get_secret("OPENAIPW").value)
    access_token = auth.get_access_token()
    return access_token


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
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://llms2155671127.vault.azure.net/", credential=credential)
    key = client.get_secret("ENCRYPTIONKEY").value

    cipher_suite = Fernet(key)
    cookie_header = req.headers.get('Cookie')
    cookies = []
    if cookie_header:
        if "PID" in cookie_header:
            cookie_pairs = cookie_header.split('; ')
            for pair in cookie_pairs:
                key, value = pair.split('=', 1)
                cookie = cipher_suite.decrypt(value.encode()).decode()
                cookies.append(cookie)
    cookie_send = SimpleCookie()
    for cookie_i in cookies:
        cookie_send.load(cookie_i)
    headers = {
        "Set-Cookie": SimpleCookie('PID='+json.dumps(cookies)),
    }
    response = func.HttpResponse(body="", status_code=200, headers=headers)

    return response

