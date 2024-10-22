from abc import ABC, abstractmethod


class BaseService(ABC):
    def __init__(self, model):
        self.s2t = model

    @abstractmethod
    def transcribe(self, path_to_wav_file: str):
        """
        Abstract method to process audio files (in wav format) to text
        """
        pass


class WhisperService(BaseService):
    _BASE_MODEL_TYPE = 'base'

    def __init__(self, model_type: str = _BASE_MODEL_TYPE) -> None:
        import whisper

        model = whisper.load_model(model_type)
        super().__init__(model)

    def use_model(self, path_to_wav_file: str, language=None):
        return self.s2t.transcribe(path_to_wav_file, language=language)

    def transcribe(self, path_to_wav_file: str, language=None) -> str:
        result = self.use_model(path_to_wav_file, language=language)
        return result['text']

    def get_no_speech_prob(self, path_to_wav_file: str, language=None) -> float:
        result = self.use_model(path_to_wav_file, language=language)
        segments = result['segments']

        if not segments:
            return 0
        if len(segments) == 0:
            return 0

        no_speech_prob_sum = 0
        for segment in segments:
            no_speech_prob_sum += segment['no_speech_prob']

        return no_speech_prob_sum / len(segments)
