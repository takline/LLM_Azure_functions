from typing import Callable, List, Optional
import requests
import json
from ...core.main import ChatMessage
from ..llm import LLM

CHAT_MODELS = {"gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-4", "gpt-3.5-turbo-0613"}
MAX_TOKENS_FOR_MODEL = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16_384,
    "gpt-4": 8192,
    "gpt-35-turbo-16k": 16_384,
    "gpt-35-turbo-0613": 4096,
    "gpt-35-turbo": 4096,
    "gpt-4-32k": 32_768,
}

def run_azure_api(input_body):
    chunks = Azure.split_to_chunks(json.dumps(input_body), Azure.ENCRYPTIONKEY)
    response = requests.post('http://localhost:7071/api/HttpTrigger1', cookies=chunks)
    encrypted_output = Azure.parse_to_dict(response.text)
    decrypted_output_str = Azure.combine_from_chunks(encrypted_output, Azure.ENCRYPTIONKEY)
    return json.loads(decrypted_output_str)

class OpenAI(LLM):
    def start(self, unique_id: Optional[str] = None, write_log: Callable[[str], None] = None):
        super().start(write_log=write_log, unique_id=unique_id)
        self.context_length = MAX_TOKENS_FOR_MODEL.get(self.model, 4096)

    def collect_args(self, options):
        args = super().collect_args(options)
        if self.engine is not None:
            args["engine"] = self.engine

        if not args["model"].endswith("0613") and "functions" in args:
            del args["functions"]

        return args

    def _stream_complete(self, prompt, options):
        args = self.collect_args(options)
        args["stream"] = True

        response = run_azure_api({
            "messages": [{"role": "user", "content": prompt}],
            **args,
        })
        
        for choice in response.get('choices', []):
            if "message" in choice:
                yield choice["message"]["content"]

    def _stream_chat(self, messages: List[ChatMessage], options):
        args = self.collect_args(options)
        args["stream"] = True

        response = run_azure_api({
            "messages": messages,
            "stream": True,
            **args,
        })

        for choice in response.get('choices', []):
            if "message" in choice:
                yield choice["message"]["content"]

    def _complete(self, prompt: str, options):
        args = self.collect_args(options)

        response = run_azure_api({
            "messages": [{"role": "user", "content": prompt}],
            **args,
        })

        return response["choices"][0]["message"]["content"]
