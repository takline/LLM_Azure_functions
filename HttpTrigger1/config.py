from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import openai
from cryptography.fernet import Fernet
import logging
from datetime import datetime


VAULT_URL = "https://llms2155671127.vault.azure.net/"
CREDENTIAL = DefaultAzureCredential()
CLIENT = SecretClient(vault_url=VAULT_URL, credential=CREDENTIAL)
ENCRYPTIONKEY = CLIENT.get_secret("ENCRYPTIONKEY").value
AWSBUCKET = CLIENT.get_secret("AWSBUCKET").value
AWSFILE = CLIENT.get_secret("AWSFILE").value
AWSSECRET = CLIENT.get_secret("AWSSECRET").value
AWSKEYID = CLIENT.get_secret("AWSKEYID").value
OPENAIKEY = CLIENT.get_secret("OPENAIKEY").value
CIPHER_SUITE = Fernet(ENCRYPTIONKEY)

HEADERS_RESPONSE = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Timing-Allow-Origin": "*"
}


HEADERS_REQUEST = {
    "Report-To": "",
    "Strict-Transport-Security": "",
    "Timing-Allow-Origin": "",
    "Vary": "",
    "X-Azure-Ref": "",
    "X-Cache": "",
    "X-Content-Type-Options": "",
    "X-Ms-Content-Source": "",
    "X-Ms-Version": "",
    "X-Ua-Compatible": "",
    "X-Xss-Protection": "",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "MicrosoftApplicationsTelemetryDeviceId=e7c5t0c7-da6d-4763-a41a-341134caf4a3; MSFPC=GUID=7de6351425f64ae3ac57a4f655ffc7fa&HASH=7de6&LV=202307&V=4&LU=1690814652902; browserId=4601243f-3cf5-47cd-8522-9cf4bge7337a; portalId=4601243f-3cf5-47cd-8522-9fs4bae7337a; ai_session=lxZ+S9sPqeVLvIk9Xpl2sY|s693935584394|1693935584394",
    "DNT": "1",
    "Host": "portal.azure.com",
    "Origin": "https",
    "Pragma": "no-cache",
    "Referer": "https",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "cors",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
}


def authenticated_openai_call(service_function, **kwargs):
    # Authenticate OpenAI
    openai.api_key = OPENAIKEY

    # Call the service function
    return service_function(**kwargs)


SERVICE_DISPATCHER = {
    "openai.ChatCompletion.create": lambda **kwargs: authenticated_openai_call(
        openai.ChatCompletion.create, **kwargs
    ),
    "openai.Audio.transcribe": lambda **kwargs: authenticated_openai_call(
        openai.Audio.transcribe, **kwargs
    ),
    # Add more services as needed
}