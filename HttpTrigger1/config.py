from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import openai
from cryptography.fernet import Fernet
import logging
from datetime import datetime
import boto3
from . import claude_authenticated

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
    "Timing-Allow-Origin": "*",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "X-UA-Compatible": "IE=edge",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "DNT": "1",
    "Referer": "https",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Cookie": "MicrosoftApplicationsTelemetryDeviceId=e7c5t0c7-da6d-4763-a41a-341134caf4a3; MSFPC=GUID=7de6351425f64ae3ac57a4f655ffc7fa&HASH=7de6&LV=202307&V=4&LU=1690814652902; browserId=4601243f-3cf5-47cd-8522-9cf4bge7337a; portalId=4601243f-3cf5-47cd-8522-9fs4bae7337a; ai_session=lxZ+S9sPqeVLvIk9Xpl2sY|s693935584394|1693935584394",
    "Server": "Apache",
    "Date": (datetime.now().strftime("%d %b %Y %H")),
    "Pragma": "no-cache",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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


def extract_session_key():
    # Initialize S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWSKEYID,
        aws_secret_access_key=AWSSECRET
    )

    # Fetch file from S3
    s3_object = s3.get_object(Bucket=AWSBUCKET, Key=AWSFILE)
    file_content = s3_object["Body"].read().decode("utf-8")

    session_key_flag = False
    session_key_value = None

    for line in file_content.splitlines():
        line = line.strip()
        if session_key_flag and line.startswith("Value:"):
            session_key_value = line.split(":", 1)[1].strip()
            break
        if line == "Name:sessionKey":
            session_key_flag = True

    return session_key_value


SERVICE_DISPATCHER = {
    "openai.ChatCompletion.create": lambda **kwargs: authenticated_openai_call(
        openai.ChatCompletion.create, **kwargs
    ),
    "openai.Audio.transcribe": lambda **kwargs: authenticated_openai_call(
        openai.Audio.transcribe, **kwargs
    ),
    "claude2": lambda **kwargs: authenticated_openai_call(
        claude_authenticated.create, **kwargs
    )
    # Add more services as needed
}
