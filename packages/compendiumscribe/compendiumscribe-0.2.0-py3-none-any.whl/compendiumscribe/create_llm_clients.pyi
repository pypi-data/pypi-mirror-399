from openai import OpenAI

__all__ = ['create_openai_client', 'MissingAPIKeyError']

class MissingAPIKeyError(RuntimeError): ...

def create_openai_client(*, timeout: int | None = None) -> OpenAI: ...
