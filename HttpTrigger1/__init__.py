import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
dir_path, func_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, dir_path)
import logging
import azure.functions as func
from cryptography.fernet import Fernet
import zlib
from typing import Union
import json
from datetime import datetime
import boto3
from . import config
from . import data_transformations

def create_httpresponse_from_dict(data: dict) -> func.HttpResponse:
    # Map the dictionary keys to match HttpResponse parameters
    return func.HttpResponse(
        body=data, headers=config.HEADERS_RESPONSE.copy(), status_code=200
    )

def upload_encrypted_data(input_data):
    bytes_data = (json.dumps(input_data)).encode('utf-8')

    s3 = boto3.resource('s3',
                             aws_access_key_id=config.AWSKEYID,
                             aws_secret_access_key=config.AWSSECRET)
    object = s3.Object(config.AWSBUCKET, config.AWSFILE)
    object.put(Body=bytes_data)

    logging.info("File uploaded successfully.")
    return "File uploaded successfully."

def main(req: func.HttpRequest) -> func.HttpResponse:
    for header in req.headers:
        logging.info(f'HEADER KEY {header}')
        logging.info(f'HEADER VALUE {req.headers[header]}')
    logging.info(req.get_body().decode("utf-8"))
    cookie_header = req.headers.get("Cookie")
    if cookie_header is None:
        cookie_header = req.get_body().decode("utf-8")
        if cookie_header is None:
            return func.HttpResponse(status_code=400)
        cookies1 = json.loads(cookie_header)
    else:
        cookies1 = data_transformations.parse_to_dict(cookie_header)
    
    cookies2 = data_transformations.combine_from_chunks(cookies1, config.ENCRYPTIONKEY)
    cookies3 = json.loads(cookies2)

    service_name = cookies3.get("service")
    if service_name not in config.SERVICE_DISPATCHER:
        return func.HttpResponse(f"Invalid service: {service_name}", status_code=400)

    # Prepare request for the specified service
    service_request = {
        "model": cookies3.get("model"),
        "messages": cookies3.get("messages", []),
    }

    # Call the service and get the response
    service_response = config.SERVICE_DISPATCHER[service_name](**service_request)
    logging.info("service_response " + json.dumps(service_response))
    # Use split_to_chunks to chunk the response
    chunked_response = data_transformations.split_to_chunks(
        service_response, config.ENCRYPTIONKEY
    )
    upload_encrypted_data(chunked_response)
    str_dict = data_transformations.dict_to_cookie_str(chunked_response)
    logging.info("str_dict " + str_dict)

    return create_httpresponse_from_dict(str_dict)
