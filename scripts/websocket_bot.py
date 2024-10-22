import base64
import json
import os
import random
import time
import asyncio
import websockets

from src.shared.hash import md5_hash
from src.fs_manager.services import WebSocketsBotArtifactsIO
from src.generative_ai.services import LangChainService
from src.speech2text.services import WhisperService
from src.audio_formatter.services import PydubService
from src.text2speech.services import XTTSService

from config import AUDIO_CAPTURE_KEY_WORD, WS_HOST, WS_PORT

READINESS_PHRASES_FILES = [
    '3be945486bb259f472499d9af879ac8d.wav',
    '007d4202dfa5ae38e1b5140090f47c2e.wav',
    '8d2291b8c6af8c2a6f81bbd9e4a6022e.wav',
    '8e3a0a1df2a45d2ad0734de30a761994.wav',
    '14d1954b6d2b2272bf0ca840e03aa2bd.wav',
    '23e71d22ba3c8c3daca23f21274d7856.wav',
    '66b26aad7ce0746f1cb19ae5f82fbed1.wav',
    '87abd187363e74cbc9aafb11ecb66420.wav',
    '4017f52f65fefdfd09123a3754048e21.wav',
    'aea108281140139cbedfd6ced91c9ed5.wav',
    'c0c6cf031b766f9652548b83f05d6e02.wav',
    'c107e2ce93aee12e68107b54c50706e7.wav',
]


class WebSocketsBot:
    _WS_TIME_THRESHOLD = 2
    _RMS_THRESHOLD = 0.5
    _NO_SPEECH_OFFSET_THRESHOLD = 1

    def __init__(self):
        self.websocket = None

        self.speech_to_text = WhisperService()
        self.text_to_speech = XTTSService()
        self.fs_manager = WebSocketsBotArtifactsIO()

        self.formatter = PydubService()
        self.langchain = LangChainService()

        self.input_webm_buffer = []
        self.input_filename_buffer = []
        self.capture_voice_query = False
        self.transcribe_voice_query = False
        self.fe_answer_waiting = False
        self.last_time_voice_collected = time.time()
        self.no_speech_offset = 0

    def start(self):
        asyncio.run(self.run_web_sockets())

    async def run_web_sockets(self):
        async with websockets.serve(self.handler, WS_HOST, WS_PORT):
            await asyncio.Future()

    async def handler(self, websocket):
        self.websocket = websocket
        async for message in websocket:
            if isinstance(message, str):
                self.fe_answer_waiting = False

            if isinstance(message, bytes):
                await self.audio_collector(message)

    async def audio_collector(self, ws_message):
        self.buffering_voice(ws_message)
        if self.fe_answer_waiting == True:
            return
        if not self.is_time_to_collect_voice():
            return
        await self.write_collected_voice()
        if not self.is_enough_voice_files_to_handle():
            return
        await self.handle_voice()

    def buffering_voice(self, ws_message):
        self.input_webm_buffer.append(ws_message)

    def is_time_to_collect_voice(self, ws_time_threshold=_WS_TIME_THRESHOLD):
        current_time = time.time()
        if current_time - self.last_time_voice_collected < ws_time_threshold:
            return False
        self.last_time_voice_collected = current_time
        return True

    async def write_collected_voice(self):
        filename = f'{self.last_time_voice_collected}.webm'
        webm_file = await self.fs_manager.write_ws_audio_file(filename, self.input_webm_buffer)
        self.input_filename_buffer.append(webm_file)

    def is_enough_voice_files_to_handle(self):
        return len(self.input_filename_buffer)

    async def handle_voice(self):
        try:
            raw_input_file_path = self.get_raw_voice_data()
            wav_input_file_path = self.formatter.processing(raw_input_file_path, '.wav')
            if self.transcribe_voice_query:
                raise
            if self.capture_voice_query:
                text = self.handle_voice_query(wav_input_file_path)
                await self.handle_gpt_prompt(text)
            else:
                is_key_word = self.handle_key_word(wav_input_file_path)
                await self.answer_with_readiness_phrase(is_key_word)
        except:
            pass
        finally:
            self.delete_file(wav_input_file_path)
            self.delete_file(raw_input_file_path)
            self.clear_raw_data_buffer()

    async def handle_gpt_prompt(self, text_message):
        if not text_message:
            return
        for text_sentence in self.langchain.ask_model(text_message):
            await self.produce_voice_messages(text_sentence)

    async def produce_voice_messages(self, text_sentence):
        sentence_hash = md5_hash(text_sentence)
        wav_ai_answer_filepath = self.fs_manager.make_ws_artifact_file_path(filename=f'{sentence_hash}.wav')
        self.text_to_speech.processing(wav_ai_answer_filepath, text_sentence)
        await self.send_voice_message(wav_ai_answer_filepath)
        self.delete_file(wav_ai_answer_filepath)

    async def send_voice_message(self, wav_ai_answer_filepath, type='stream'):
        with open(wav_ai_answer_filepath, 'rb') as file:
            data = file.read()
            if self.websocket:
                audio_base64 = base64.b64encode(data).decode('utf-8')
                data_json = {'type': type, 'data': audio_base64}
                await self.websocket.send(json.dumps(data_json))

    def get_raw_voice_data(self):
        return self.input_filename_buffer.pop(0)

    def clear_raw_data_buffer(self):
        self.input_webm_buffer = self.input_webm_buffer[:1]

    def handle_voice_query(self, output_file_path):
        if self.is_enough_speech(output_file_path):
            self.clear_no_speech_offset()
            audio = self.formatter.read_audio_from_file(output_file_path)
            self.write_spec_wav(audio)
            return None
        else:
            if self.is_necessary_to_postpone_transcribing():
                return None

        self.transcribe_voice_query = True
        try:
            return self.transcribe_query()
        except:
            pass
        finally:
            self.capture_voice_query = False
            self.transcribe_voice_query = False

    def clear_no_speech_offset(self):
        self.no_speech_offset = 0

    def is_necessary_to_postpone_transcribing(self, no_speech_offset_threshold=_NO_SPEECH_OFFSET_THRESHOLD):
        print(f'Postpone {self.no_speech_offset}')
        if self.no_speech_offset < no_speech_offset_threshold:
            self.no_speech_offset += 1
            return True
        else:
            self.no_speech_offset = 0
            return False

    def transcribe_query(self):
        print('Start Transcribing')
        special_wav = self.fs_manager.get_spec_file()
        text = self.speech_to_text.transcribe(special_wav, language='ru')
        print(f'Finish transcribing')
        self.delete_file(special_wav)
        return text

    def handle_key_word(self, input_file_path):
        try:
            text = self.speech_to_text.transcribe(input_file_path, language='ru')
            if text:
                if AUDIO_CAPTURE_KEY_WORD in text:
                    self.capture_voice_query = True
                    print('Start Listen')
                    return True
        except Exception as error:
            print(error)

    def is_enough_speech(self, file_path, rms_threshold=_RMS_THRESHOLD):
        no_speech_prob = self.speech_to_text.get_no_speech_prob(file_path)
        return no_speech_prob < rms_threshold

    def write_spec_wav(self, audio):
        special_wav = self.fs_manager.get_spec_file()
        try:
            audio_origin = self.formatter.read_audio_from_file(special_wav)
            self.formatter.write_audio_into_file(special_wav, audio_origin + audio)
        except:
            self.formatter.write_audio_into_file(special_wav, audio)

    @staticmethod
    def delete_file(file_path):
        if not os.path.exists(file_path):
            print(f'Cant find file to delete {file_path}')
            return
        try:
            os.remove(file_path)
        except Exception as e:
            print(f'Cannot delete {file_path}: {e}')

    def get_readiness_phrase_file(self, phrases_wav=READINESS_PHRASES_FILES):
        phrase_wav_file = random.choice(phrases_wav)
        return f'sentences/{phrase_wav_file}'

    async def answer_with_readiness_phrase(self, is_key_word):
        if not is_key_word:
            return
        readiness_phrase_wav = self.get_readiness_phrase_file()
        await self.send_voice_message(readiness_phrase_wav, 'greetings')
        self.fe_answer_waiting = True


if __name__ == '__main__':
    ws_bot = WebSocketsBot()
    ws_bot.start()
