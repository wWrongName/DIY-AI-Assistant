from abc import ABC, abstractmethod

import torch

from config import TTS_XTTS_MODEL, TTS_XTTS_SPEAKER, TTS_XTTS_LANGUAGE


class BaseService(ABC):
    def __init__(self, model):
        self.t2s = model

    @abstractmethod
    def processing(self, text: str):
        """
        Abstract method to process text to audio files (in wav format)
        """
        pass


class XTTSService(BaseService):
    _BASE_MODEL_TYPE = TTS_XTTS_MODEL
    _BASE_MODEL_SPEAKER = TTS_XTTS_SPEAKER
    _BASE_MODEL_LANGUAGE = TTS_XTTS_LANGUAGE

    def __init__(self, model_type: str = _BASE_MODEL_TYPE) -> None:
        from TTS.api import TTS

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f'Apply {device} device for XTTS calculations')

        model = TTS(model_type).to(device)

        super().__init__(model)

    def processing(
        self,
        path_to_output_wav: str,
        text: str,
        language: str = _BASE_MODEL_LANGUAGE,
        speaker: str = _BASE_MODEL_SPEAKER,
    ):
        self.t2s.tts_to_file(text=text, file_path=path_to_output_wav, language=language, speaker=speaker, speed=2)
