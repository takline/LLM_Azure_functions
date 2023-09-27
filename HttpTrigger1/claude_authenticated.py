from . import config
from . import claude

def create(model, messages):
    cookie = "sessionKey="+config.extract_session_key()
    client = claude.Claude(cookie)
    if model!="continue":
        client.create_new_conversation()
    response=client.get_answer(messages)
    return response