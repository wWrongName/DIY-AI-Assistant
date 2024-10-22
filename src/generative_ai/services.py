import re
from langchain_ollama import ChatOllama

from config import LLM_MODEL


class LangChainService:
    _BASE_MODEL = LLM_MODEL

    def __init__(self, model_type: str = _BASE_MODEL):
        self.model = ChatOllama(model=model_type)
        self.context = ''

    def ask_model(self, question: str):
        buffer = ''
        sentence_end_pattern = re.compile(r'[.!?]')

        for chunk in self.model.stream(f'{self.context}\n{question}'):
            buffer += str(chunk.content)
            while True:
                match = sentence_end_pattern.search(buffer)
                if match:
                    end_idx = match.end()
                    sentence = buffer[:end_idx].strip()
                    sentence = sentence[0 : len(sentence) - 1]
                    yield sentence
                    buffer = buffer[end_idx:].strip()
                else:
                    break
