from abc import ABC, abstractmethod
import os

from src.shared.exceptions import DoNotImplementedException


class BaseService(ABC):
    def __init__(self, model):
        self.formatter = model

    def processing(self, input_file_path: str, output_file_extension: str):
        audio = self.read_audio_from_file(input_file_path)

        file_path_name, _ = self.get_file_partitions(input_file_path)
        output_file_path = f'{file_path_name}{output_file_extension}'

        self.write_audio_into_file(output_file_path, audio)
        return output_file_path

    @staticmethod
    def get_file_partitions(file_path: str):
        file_path_name, file_extension = os.path.splitext(file_path)
        return file_path_name, file_extension

    def read_audio_from_file(self, input_file_path: str):
        _, file_extension = self.get_file_partitions(input_file_path)
        if file_extension == '.ogg':
            return self.read_ogg_file(input_file_path)
        elif file_extension == '.wav':
            return self.read_wav_file(input_file_path)
        elif file_extension == '.webm':
            return self.read_webm_file(input_file_path)
        else:
            raise Exception

    @abstractmethod
    def read_ogg_file(self, input_file_path):
        raise DoNotImplementedException()

    @abstractmethod
    def read_wav_file(self, input_file_path):
        raise DoNotImplementedException()

    @abstractmethod
    def read_webm_file(self, input_file_path):
        raise DoNotImplementedException()

    def write_audio_into_file(self, output_file_path: str, audio):
        _, file_extension = self.get_file_partitions(output_file_path)
        if file_extension == '.wav':
            self.write_wav_file(output_file_path, audio)
        elif file_extension == '.ogg':
            self.write_ogg_file(output_file_path, audio)
        else:
            raise Exception

    @abstractmethod
    def write_wav_file(self, output_file_path: str, audio):
        raise DoNotImplementedException()

    @abstractmethod
    def write_ogg_file(self, output_file_path: str, audio):
        raise DoNotImplementedException()


class PydubService(BaseService):
    def __init__(self) -> None:
        from pydub import AudioSegment

        super().__init__(AudioSegment)

    def read_ogg_file(self, input_file_path):
        audio = self.formatter.from_ogg(input_file_path)
        return audio

    def read_wav_file(self, input_file_path):
        audio = self.formatter.from_wav(input_file_path)
        return audio

    def read_webm_file(self, input_file_path):
        audio = self.formatter.from_file(input_file_path, format="webm")
        return audio

    def write_wav_file(self, output_file_path: str, audio):
        audio.export(output_file_path, format="wav")

    def write_ogg_file(self, output_file_path: str, audio):
        audio.export(output_file_path, format="ogg")
